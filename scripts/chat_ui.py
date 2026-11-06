"""
Groupware AI Chatbot - Web UI Server with Retrieval & QA Agent.
Powered by FastAPI, vLLM (Qwen2.5-7B-Instruct), Qdrant Native Server, and PostgreSQL.
"""

import sys
import json
import logging
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from pydantic import BaseModel

# Add workspace root to sys.path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from etl.config import config
from etl.llm_client import LLMClient
from etl.agents.retrieval_qa_agent import RetrievalQAAgent

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("chat_ui")

app = FastAPI(title="Groupware AI Chatbot - Retrieval & QA Agent")

# Khởi tạo Agent
qa_agent = RetrievalQAAgent()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    use_rag: bool = True
    tenant_id: int = 1
    top_k: int = 4
    temperature: float = 0.1
    max_tokens: int = 2048
    model: Optional[str] = None

HTML_PAGE = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agent Truy Xuất & Hỏi Đáp - Groupware AI</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Marked.js for Markdown parsing -->
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <style>
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: #0f172a; }
        ::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #475569; }
        .chat-container { scroll-behavior: smooth; }
        pre code { border-radius: 0.5rem; }
        .prose pre { padding: 0.75rem; background: #090d16; }
        .prose p { margin-bottom: 0.5rem; }
        .prose p:last-child { margin-bottom: 0; }
        .prose table { width: 100%; border-collapse: collapse; margin: 0.75rem 0; font-size: 0.85rem; }
        .prose th, .prose td { border: 1px solid #334155; padding: 0.4rem 0.6rem; text-align: left; }
        .prose th { background-color: #1e293b; color: #38bdf8; font-weight: 600; }
        .typing-cursor::after {
            content: '▌';
            display: inline-block;
            animation: blink 0.8s infinite;
            color: #38bdf8;
        }
        @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
    </style>
</head>
<body class="bg-slate-950 text-slate-100 flex h-screen font-sans overflow-hidden antialiased">

    <!-- SIDEBAR -->
    <aside class="w-80 bg-slate-900 border-r border-slate-800 flex flex-col justify-between p-4 select-none">
        <div>
            <!-- Header / Brand -->
            <div class="flex items-center gap-3 pb-4 border-b border-slate-800">
                <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center font-black text-xl text-white shadow-lg shadow-sky-500/20">
                    QA
                </div>
                <div>
                    <h1 class="font-bold text-base tracking-wide text-white">Agent Truy Xuất & Hỏi Đáp</h1>
                    <p class="text-xs text-sky-400 font-medium">Retrieval & Analytics Agent</p>
                </div>
            </div>

            <!-- Health Status Badge -->
            <div id="vllm-status-box" class="mt-4 p-2.5 rounded-lg bg-slate-800/60 border border-slate-700/60 flex items-center justify-between text-xs">
                <span class="text-slate-400 font-medium">vLLM Inference:</span>
                <span id="vllm-badge" class="flex items-center gap-1.5 text-amber-400 font-semibold">
                    <span class="w-2 h-2 rounded-full bg-amber-400 animate-pulse"></span> Đang kiểm tra...
                </span>
            </div>

            <!-- Capabilities list -->
            <div class="mt-4 p-3 bg-slate-800/40 border border-slate-700/40 rounded-xl text-xs space-y-2">
                <div class="font-semibold text-slate-300 flex items-center gap-1.5">
                    <span class="w-2 h-2 rounded-full bg-emerald-400"></span> Năng lực Agent tích hợp:
                </div>
                <div class="text-slate-400 text-[11px] space-y-1">
                    <div>⚡ <strong>Text-to-SQL Engine:</strong> Tự động tính toán, đếm số lượng, tổng hợp dữ liệu từ PostgreSQL.</div>
                    <div>📚 <strong>Vector Semantic KB:</strong> Tra cứu quy chế, thông báo qua Qdrant Server.</div>
                    <div>🛡️ <strong>Safety Guardrails:</strong> Giám sát truy vấn chỉ đọc SELECT, bảo mật tuyệt đối.</div>
                </div>
            </div>

            <!-- Settings Form -->
            <div class="mt-4 space-y-3.5 text-xs">
                <div>
                    <label class="block font-medium text-slate-300 mb-1">Mô hình (Model)</label>
                    <input id="input-model" type="text" value="Qwen/Qwen2.5-7B-Instruct-AWQ" 
                        class="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-slate-200 focus:outline-none focus:border-sky-500">
                </div>

                <div class="flex items-center justify-between p-2.5 bg-slate-800/40 border border-slate-700/40 rounded-lg">
                    <div>
                        <span class="font-medium text-slate-200 block">Agent Truy Xuất Tự Động</span>
                        <span class="text-[11px] text-slate-400">Bật truy vấn SQL + Vector</span>
                    </div>
                    <label class="relative inline-flex items-center cursor-pointer">
                        <input id="toggle-rag" type="checkbox" checked class="sr-only peer">
                        <div class="w-9 h-5 bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-sky-500"></div>
                    </label>
                </div>

                <div class="grid grid-cols-2 gap-2">
                    <div>
                        <label class="block font-medium text-slate-300 mb-1">Tenant ID</label>
                        <input id="input-tenant" type="number" value="1" min="1" 
                            class="w-full bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-sky-500">
                    </div>
                    <div>
                        <label class="block font-medium text-slate-300 mb-1">Top-K Vector</label>
                        <input id="input-topk" type="number" value="4" min="1" max="10" 
                            class="w-full bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-sky-500">
                    </div>
                </div>

                <div>
                    <div class="flex justify-between items-center mb-1">
                        <label class="font-medium text-slate-300">Temperature</label>
                        <span id="temp-val" class="text-slate-400">0.1</span>
                    </div>
                    <input id="input-temp" type="range" min="0" max="1" step="0.05" value="0.1"
                        class="w-full accent-sky-500 cursor-pointer"
                        oninput="document.getElementById('temp-val').innerText = this.value">
                </div>
            </div>
        </div>

        <!-- Footer / Action Buttons -->
        <div class="space-y-2 pt-3 border-t border-slate-800">
            <button onclick="clearChat()" class="w-full py-2 bg-slate-800 hover:bg-slate-700 active:bg-slate-700/80 text-slate-200 font-medium text-xs rounded-lg transition border border-slate-700/60 flex items-center justify-center gap-2">
                <svg class="w-3.5 h-3.5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                Xóa lịch sử trò chuyện
            </button>
            <div class="text-[11px] text-center text-slate-500">
                Groupware Single Unified QA Agent v2.0
            </div>
        </div>
    </aside>

    <!-- MAIN CHAT AREA -->
    <main class="flex-1 flex flex-col h-full overflow-hidden bg-slate-950">
        
        <!-- TOP STATUS / BANNER -->
        <header class="h-14 border-b border-slate-800/80 px-6 flex items-center justify-between bg-slate-900/40 backdrop-blur-sm">
            <div class="flex items-center gap-3">
                <div class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></div>
                <span class="text-sm font-semibold text-slate-200">Agent Truy Xuất, Hỏi Đáp & Tính Toán Doanh Nghiệp</span>
            </div>
            <div class="flex items-center gap-3 text-xs text-slate-400">
                <span>Doanh nghiệp: <strong id="header-tenant" class="text-sky-400 font-medium">Tenant #1</strong></span>
                <span class="text-slate-600">|</span>
                <span id="header-rag-badge" class="px-2 py-0.5 rounded bg-sky-950/70 border border-sky-800 text-sky-300 text-[11px] font-medium">AGENT ACTIVE</span>
            </div>
        </header>

        <!-- CHAT MESSAGES SCROLL AREA -->
        <div id="chat-box" class="chat-container flex-1 overflow-y-auto p-6 space-y-6">
            <!-- Initial Assistant Greeting -->
            <div class="flex gap-4 max-w-4xl">
                <div class="w-8 h-8 rounded-lg bg-sky-600 flex-shrink-0 flex items-center justify-center text-white font-bold text-xs shadow-md shadow-sky-600/20">
                    AI
                </div>
                <div class="flex-1">
                    <div class="bg-slate-900 border border-slate-800 rounded-2xl rounded-tl-none p-4 text-sm text-slate-200 shadow-sm leading-relaxed prose prose-invert max-w-none">
                        Xin chào! Tôi là <strong>Agent Truy Xuất & Hỏi Đáp</strong> của hệ thống Groupware.<br><br>
                        Tôi được tích hợp sẵn 2 công cụ cốt lõi:
                        <ul class="list-disc pl-5 mt-2 space-y-1 text-slate-300">
                            <li><strong>Công cụ tính toán & thống kê cơ sở dữ liệu (SQL Engine):</strong> Đếm số lượng đơn phê duyệt của nhân viên, thống kê phòng ban, danh sách dự án, tài sản thiết bị, phép năm chính xác 100%.</li>
                            <li><strong>Công cụ tra cứu tri thức (Semantic KB):</strong> Tìm kiếm quy chế công ty, thông báo nội bộ, tin nhắn thảo luận.</li>
                        </ul>
                        <div class="mt-3 p-2 bg-slate-800/60 rounded-lg text-xs text-slate-400">
                            💡 <em>Gợi ý câu hỏi thử nghiệm:</em><br>
                            - "Nhân viên Đặng Thị Huyền Trang có bao nhiêu đơn phê duyệt?"<br>
                            - "Công ty hiện tại có bao nhiêu nhân viên và phòng ban?"<br>
                            - "Hoàng Việt Nam Ly có bao nhiêu đơn phê duyệt và trạng thái thế nào?"
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- INPUT BOX AREA -->
        <div class="p-4 border-t border-slate-800 bg-slate-900/50">
            <div class="max-w-4xl mx-auto relative">
                <form id="chat-form" onsubmit="handleSend(event)" class="relative flex items-center">
                    <textarea id="user-input" rows="1" placeholder="Hỏi tôi bất kỳ điều gì về nhân sự, đơn phê duyệt, dự án, quy chế... (Enter để gửi)"
                        class="w-full bg-slate-900 border border-slate-700/80 rounded-xl pl-4 pr-24 py-3.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500 resize-none transition"
                        onkeydown="if(event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); handleSend(event); }"></textarea>

                    <div class="absolute right-2 flex items-center gap-1.5">
                        <button type="submit" id="send-btn"
                            class="p-2 bg-sky-500 hover:bg-sky-400 active:bg-sky-600 text-white rounded-lg transition shadow-md shadow-sky-500/20 disabled:opacity-50 disabled:cursor-not-allowed">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
                        </button>
                    </div>
                </form>
                <div class="flex justify-between items-center px-2 pt-2 text-[11px] text-slate-500">
                    <span>Mô hình nội bộ: Qwen2.5-7B-Instruct (vLLM GPU) | Cơ sở dữ liệu: PostgreSQL + Qdrant Native</span>
                    <span>Retrieval & QA Agent</span>
                </div>
            </div>
        </div>

    </main>

    <!-- JAVASCRIPT LOGIC -->
    <script>
        let chatHistory = [];
        let isGenerating = false;

        marked.setOptions({
            highlight: function(code, lang) {
                if (lang && hljs.getLanguage(lang)) {
                    return hljs.highlight(code, { language: lang }).value;
                }
                return hljs.highlightAuto(code).value;
            },
            breaks: true
        });

        async function checkServerHealth() {
            const badge = document.getElementById('vllm-badge');
            try {
                const res = await fetch('/api/health');
                const data = await res.json();
                if (data.status === 'ok') {
                    badge.className = 'flex items-center gap-1.5 text-emerald-400 font-semibold';
                    badge.innerHTML = '<span class="w-2 h-2 rounded-full bg-emerald-400"></span> Đang hoạt động';
                } else {
                    badge.className = 'flex items-center gap-1.5 text-rose-400 font-semibold';
                    badge.innerHTML = '<span class="w-2 h-2 rounded-full bg-rose-400"></span> Chưa kết nối vLLM';
                }
            } catch (e) {
                badge.className = 'flex items-center gap-1.5 text-rose-400 font-semibold';
                badge.innerHTML = '<span class="w-2 h-2 rounded-full bg-rose-400"></span> Ngoại tuyến';
            }
        }
        setInterval(checkServerHealth, 8000);
        checkServerHealth();

        document.getElementById('input-tenant').addEventListener('input', (e) => {
            document.getElementById('header-tenant').innerText = 'Tenant #' + (e.target.value || '1');
        });

        document.getElementById('toggle-rag').addEventListener('change', (e) => {
            const el = document.getElementById('header-rag-badge');
            if (e.target.checked) {
                el.innerText = 'AGENT ACTIVE';
                el.className = 'px-2 py-0.5 rounded bg-sky-950/70 border border-sky-800 text-sky-300 text-[11px] font-medium';
            } else {
                el.innerText = 'AGENT OFF';
                el.className = 'px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-400 text-[11px] font-medium';
            }
        });

        function clearChat() {
            chatHistory = [];
            const chatBox = document.getElementById('chat-box');
            chatBox.innerHTML = `
                <div class="flex gap-4 max-w-4xl">
                    <div class="w-8 h-8 rounded-lg bg-sky-600 flex-shrink-0 flex items-center justify-center text-white font-bold text-xs shadow-md shadow-sky-600/20">AI</div>
                    <div class="flex-1">
                        <div class="bg-slate-900 border border-slate-800 rounded-2xl rounded-tl-none p-4 text-sm text-slate-200 shadow-sm leading-relaxed prose prose-invert max-w-none">
                            Lịch sử trò chuyện đã được làm mới. Bạn muốn tra cứu hoặc tính toán dữ liệu gì tiếp theo?
                        </div>
                    </div>
                </div>
            `;
        }

        function scrollToBottom() {
            const box = document.getElementById('chat-box');
            box.scrollTop = box.scrollHeight;
        }

        async function handleSend(e) {
            e.preventDefault();
            if (isGenerating) return;

            const inputEl = document.getElementById('user-input');
            const text = inputEl.value.trim();
            if (!text) return;

            inputEl.value = '';
            inputEl.style.height = 'auto';

            // Append User Message to UI
            appendUserMessage(text);
            chatHistory.push({ role: 'user', content: text });

            // Prepare Assistant Placeholder
            const assistantId = 'resp_' + Date.now();
            appendAssistantSkeleton(assistantId);
            scrollToBottom();

            isGenerating = true;
            document.getElementById('send-btn').disabled = true;

            const payload = {
                messages: chatHistory,
                use_rag: document.getElementById('toggle-rag').checked,
                tenant_id: parseInt(document.getElementById('input-tenant').value || '1'),
                top_k: parseInt(document.getElementById('input-topk').value || '4'),
                temperature: parseFloat(document.getElementById('input-temp').value || '0.1'),
                model: document.getElementById('input-model').value.trim()
            };

            let accumulatedText = '';
            const contentEl = document.getElementById(`${assistantId}_content`);
            const sqlEl = document.getElementById(`${assistantId}_sql`);
            const citationsEl = document.getElementById(`${assistantId}_citations`);

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (!response.ok) {
                    throw new Error(`HTTP Error ${response.status}`);
                }

                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';

                contentEl.classList.add('typing-cursor');

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    buffer += decoder.decode(value, { stream: true });
                    const lines = buffer.split('\\n');
                    buffer = lines.pop();

                    for (const line of lines) {
                        const trimmed = line.trim();
                        if (trimmed.startsWith('data: ')) {
                            const rawData = trimmed.slice(6);
                            if (rawData === '[DONE]') continue;

                            try {
                                const parsed = JSON.parse(rawData);
                                if (parsed.event === 'delta') {
                                    accumulatedText += parsed.text;
                                    contentEl.innerHTML = marked.parse(accumulatedText);
                                    scrollToBottom();
                                } else if (parsed.event === 'sql_info') {
                                    renderSqlInfo(sqlEl, parsed.sql, parsed.count);
                                    scrollToBottom();
                                } else if (parsed.event === 'citations') {
                                    renderCitations(citationsEl, parsed.citations);
                                    scrollToBottom();
                                } else if (parsed.event === 'error') {
                                    contentEl.innerHTML = `<span class="text-rose-400 font-medium">⚠️ ${parsed.message}</span>`;
                                }
                            } catch (err) {
                                console.error('Parse chunk error', err);
                            }
                        }
                    }
                }

                contentEl.classList.remove('typing-cursor');
                chatHistory.push({ role: 'assistant', content: accumulatedText });

            } catch (err) {
                contentEl.classList.remove('typing-cursor');
                contentEl.innerHTML = `
                    <div class="p-3 rounded-lg bg-rose-950/60 border border-rose-800 text-rose-300 text-xs">
                        <strong>Lỗi kết nối tới Agent / vLLM Server!</strong><br>
                        Vui lòng chắc chắn rằng vLLM và PostgreSQL đang hoạt động bình thường.<br>
                        Chi tiết: ${escapeHtml(err.message)}
                    </div>
                `;
            } finally {
                isGenerating = false;
                document.getElementById('send-btn').disabled = false;
                inputEl.focus();
            }
        }

        function appendUserMessage(text) {
            const chatBox = document.getElementById('chat-box');
            const div = document.createElement('div');
            div.className = 'flex gap-4 max-w-4xl justify-end ml-auto';
            div.innerHTML = `
                <div class="bg-sky-600 text-white rounded-2xl rounded-tr-none px-4 py-3 text-sm shadow-md leading-relaxed whitespace-pre-wrap max-w-2xl">
                    ${escapeHtml(text)}
                </div>
                <div class="w-8 h-8 rounded-lg bg-slate-800 border border-slate-700 flex-shrink-0 flex items-center justify-center text-slate-300 font-bold text-xs">
                    Tôi
                </div>
            `;
            chatBox.appendChild(div);
        }

        function appendAssistantSkeleton(id) {
            const chatBox = document.getElementById('chat-box');
            const div = document.createElement('div');
            div.className = 'flex gap-4 max-w-4xl';
            div.innerHTML = `
                <div class="w-8 h-8 rounded-lg bg-sky-600 flex-shrink-0 flex items-center justify-center text-white font-bold text-xs shadow-md shadow-sky-600/20">
                    AI
                </div>
                <div class="flex-1 space-y-2">
                    <div id="${id}_sql" class="hidden"></div>
                    <div id="${id}_citations" class="hidden"></div>
                    <div id="${id}_content" class="bg-slate-900 border border-slate-800 rounded-2xl rounded-tl-none p-4 text-sm text-slate-200 shadow-sm leading-relaxed prose prose-invert max-w-none">
                        <span class="text-slate-400">Agent đang phân tích câu hỏi và truy xuất dữ liệu...</span>
                    </div>
                </div>
            `;
            chatBox.appendChild(div);
        }

        function renderSqlInfo(container, sql, count) {
            if (!sql) return;
            container.classList.remove('hidden');
            container.innerHTML = `
                <details class="mb-2 p-2.5 bg-indigo-950/40 border border-indigo-800/60 rounded-xl text-xs" open>
                    <summary class="font-medium text-indigo-300 cursor-pointer select-none flex items-center gap-1.5 hover:text-indigo-200">
                        ⚡ <strong>Agent đã tự động truy vấn CSDL PostgreSQL</strong> (Khớp ${count} bản ghi thực tế)
                    </summary>
                    <div class="mt-2 pt-2 border-t border-indigo-900/60 space-y-1">
                        <div class="font-mono bg-slate-950 p-2 rounded text-emerald-400 text-[11px] overflow-x-auto border border-slate-800">${escapeHtml(sql)}</div>
                    </div>
                </details>
            `;
        }

        function renderCitations(container, citations) {
            if (!citations || citations.length === 0) return;
            container.classList.remove('hidden');
            let itemsHtml = '';
            citations.forEach((c, idx) => {
                itemsHtml += `
                    <div class="p-2 bg-slate-950/80 border border-slate-800 rounded text-xs space-y-1">
                        <div class="flex items-center justify-between text-[11px] text-sky-400 font-semibold">
                            <span>#${idx + 1} [${(c.source_type || 'DATA').toUpperCase()}]</span>
                            <span class="text-slate-500">Độ khớp: ${c.score}</span>
                        </div>
                        <div class="text-slate-300 line-clamp-2">${escapeHtml(c.text || '')}</div>
                    </div>
                `;
            });

            container.innerHTML = `
                <details class="mb-2 p-2 bg-slate-900/80 border border-slate-800/80 rounded-xl text-xs">
                    <summary class="font-medium text-sky-400 cursor-pointer select-none flex items-center gap-1.5 hover:text-sky-300">
                        📚 Đã tham khảo ${citations.length} tài liệu Groupware (Click để xem)
                    </summary>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-2 mt-2 pt-2 border-t border-slate-800">
                        ${itemsHtml}
                    </div>
                </details>
            `;
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.innerText = text;
            return div.innerHTML;
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def get_index():
    return HTML_PAGE

@app.get("/api/health")
async def health_check():
    """Checks whether the vLLM server is responsive."""
    import httpx
    target_url = f"{config.llm_api_base.rstrip('/v1')}/health"
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(target_url)
            if resp.status_code == 200:
                return {"status": "ok", "url": config.llm_api_base}
    except Exception:
        pass

    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(f"{config.llm_api_base}/models")
            if resp.status_code == 200:
                return {"status": "ok", "url": config.llm_api_base}
    except Exception:
        pass

    return {"status": "down", "url": config.llm_api_base}

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    """
    Điểm tiếp nhận câu hỏi người dùng:
    - Nếu bật Agent (use_rag=True): Chuyển câu hỏi cho RetrievalQAAgent xử lý.
      Agent sẽ tự phân tích ý định, thực thi SQL tính toán hoặc tra cứu Vector KB, sau đó stream câu trả lời.
    - Nếu tắt Agent: Gọi trực tiếp mô hình vLLM thuần.
    """
    async def event_generator():
        user_query = ""
        # Trích xuất câu hỏi gần nhất của người dùng
        for msg in reversed(req.messages):
            if msg.role == "user":
                user_query = msg.content
                break

        if not user_query:
            yield "data: [DONE]\n\n"
            return

        chat_history = [{"role": m.role, "content": m.content} for m in req.messages[:-1]]

        if req.use_rag:
            try:
                # Xử lý qua RetrievalQAAgent
                agent_result = qa_agent.process(
                    query=user_query,
                    chat_history=chat_history,
                    tenant_id=req.tenant_id,
                    stream=True
                )

                # 1. Báo cáo câu truy vấn SQL đã chạy nếu có
                if agent_result.get("sql_evidence"):
                    sql_info = {
                        "event": "sql_info",
                        "sql": agent_result["sql_evidence"],
                        "count": len(agent_result.get("sql_data") or [])
                    }
                    yield f"data: {json.dumps(sql_info, ensure_ascii=False)}\n\n"

                # 2. Báo cáo tài liệu tham khảo nếu có
                if agent_result.get("citations"):
                    cit_info = {
                        "event": "citations",
                        "citations": agent_result["citations"]
                    }
                    yield f"data: {json.dumps(cit_info, ensure_ascii=False)}\n\n"

                # 3. Stream từng token trả lời từ LLM
                stream_gen = agent_result.get("stream_generator")
                if stream_gen:
                    for token in stream_gen:
                        if token:
                            chunk = json.dumps({"event": "delta", "text": token}, ensure_ascii=False)
                            yield f"data: {chunk}\n\n"

                yield "data: [DONE]\n\n"
                return

            except Exception as e:
                logger.exception(f"Lỗi xử lý qua RetrievalQAAgent: {e}")
                err_msg = json.dumps({
                    "event": "error",
                    "message": f"Lỗi Agent: {str(e)}"
                }, ensure_ascii=False)
                yield f"data: {err_msg}\n\n"
                return

        # Luồng gọi LLM trực tiếp không qua Agent
        llm = LLMClient(model_name=req.model)
        try:
            stream_gen = llm.generate_chat_response(
                messages=[{"role": m.role, "content": m.content} for m in req.messages],
                temperature=req.temperature,
                max_tokens=req.max_tokens,
                stream=True
            )
            for token in stream_gen:
                if token:
                    chunk = json.dumps({"event": "delta", "text": token}, ensure_ascii=False)
                    yield f"data: {chunk}\n\n"

            yield "data: [DONE]\n\n"

        except Exception as e:
            err_msg = json.dumps({
                "event": "error",
                "message": f"Không thể kết nối vLLM server: {str(e)}"
            }, ensure_ascii=False)
            yield f"data: {err_msg}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

def main():
    parser = argparse.ArgumentParser(description="Groupware AI Chatbot - Retrieval & QA Agent")
    parser.add_argument("--host", default="0.0.0.0", help="Host address (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8080, help="Port (default: 8080)")
    args = parser.parse_args()

    print(f"\n=======================================================")
    print(f" Groupware AI - Retrieval & QA Agent Server")
    print(f" Web UI:      http://localhost:{args.port}")
    print(f" vLLM Engine: {config.llm_api_base}")
    print(f"=======================================================\n")

    uvicorn.run(app, host=args.host, port=args.port, log_level="info")

if __name__ == "__main__":
    main()
