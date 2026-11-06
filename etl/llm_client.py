"""
LLM Client Module for vLLM Serving (OpenAI-compatible API).
Supports Qwen2.5-7B-Instruct with prompt templates, streaming, and multi-tenant grounding.
"""

import logging
from typing import List, Dict, Any, Generator, Optional
from openai import OpenAI
from etl.config import config

logger = logging.getLogger("etl.llm_client")

class LLMClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None
    ):
        self.base_url = base_url or config.llm_api_base
        self.api_key = api_key or config.llm_api_key
        self.model_name = model_name or config.llm_model_name
        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)

    def generate_chat_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 2048,
        stream: bool = False
    ):
        """
        Gửi yêu cầu chat completion tới vLLM server.
        Hỗ trợ cả trả lời trực tiếp hoặc stream tokens.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )
            if stream:
                return self._stream_generator(response)
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Lỗi khi gọi LLM inference ({self.base_url}): {e}")
            raise

    def _stream_generator(self, response) -> Generator[str, None, None]:
        for chunk in response:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content

    def build_rag_prompt(
        self,
        query: str,
        retrieved_contexts: List[Dict[str, Any]],
        system_instructions: Optional[str] = None,
        company_overview: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Tạo payload prompt kết hợp ngữ cảnh từ Vector DB / Graph DB và thông tin doanh nghiệp phục vụ RAG.
        """
        if not system_instructions:
            system_instructions = (
                "Bạn là trợ lý AI thông minh chuyên nghiệp của hệ thống Groupware doanh nghiệp IQ NFFICE.\n"
                "Nhiệm vụ của bạn là hỗ trợ nhân viên giải đáp thông tin công ty, cơ cấu tổ chức, nhân sự, lịch trình, phiếu duyệt và quy định một cách chính xác, mạch lạc bằng Tiếng Việt.\n"
                "Tuân thủ các nguyên tắc sau:\n"
                "1. Dựa trên 'Thông tin tổng quan doanh nghiệp' và 'Ngữ cảnh được cung cấp' để trả lời trung thực.\n"
                "2. Trả lời rõ ràng, dùng gạch đầu dòng, nêu số liệu chính xác khi người dùng hỏi về số lượng nhân viên, phòng ban, dự án hoặc tài sản.\n"
                "3. Tuyệt đối không bịa đặt số liệu không có trong tài liệu."
            )

        context_str = ""
        if company_overview:
            context_str += f"=== THÔNG TIN DOANH NGHIỆP CỐT LÕI ===\n{company_overview}\n\n"

        if retrieved_contexts:
            context_str += "=== TÀI LIỆU TRÍCH XUẤT LIÊN QUAN ===\n"
            for i, ctx in enumerate(retrieved_contexts, 1):
                src_type = ctx.get("source_type", "unknown")
                text = ctx.get("text", "")
                context_str += f"[{i}] ({src_type.upper()}): {text}\n"

        user_content = (
            f"--- DỮ LIỆU & NGỮ CẢNH HỆ THỐNG ---\n{context_str}\n"
            f"--- CÂU HỎI CỦA NGƯỜI DÙNG ---\n{query}"
        )

        return [
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": user_content}
        ]
