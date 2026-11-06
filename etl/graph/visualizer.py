"""
Graph Ontology & Instance Visualizer Module.
Generates an interactive, standalone HTML visualizer for:
1. Architecture B Schema Ontology (24 Node Types, 43 Relationship Types)
2. Live Ingested Instance Graph (Multi-Tenant filtering, property inspector, search)
"""

import json
import logging
import webbrowser
from pathlib import Path
from typing import Dict, Any
from etl.config import config, ROOT

logger = logging.getLogger("etl.graph.visualizer")

# Canonical 24 Nodes (Ontology Metamodel)
ONTOLOGY_NODES = [
    {"id": "Tenant", "label": "Tenant (NM-01)", "group": "org", "color": "#2563eb", "desc": "Doanh nghiệp / Multi-tenant root container"},
    {"id": "User", "label": "User (NM-02)", "group": "org", "color": "#3b82f6", "desc": "Nhân viên / Định danh người dùng toàn cầu"},
    {"id": "Department", "label": "Department (NM-03)", "group": "org", "color": "#60a5fa", "desc": "Phòng ban cơ cấu tổ chức"},
    {"id": "Role", "label": "Role (NM-04)", "group": "org", "color": "#93c5fd", "desc": "Vai trò phân quyền hệ thống"},
    {"id": "Permission", "label": "Permission (NM-05)", "group": "org", "color": "#bfdbfe", "desc": "Danh mục quyền hạn chi tiết"},
    {"id": "Project", "label": "Project (NM-06)", "group": "workflow", "color": "#10b981", "desc": "Dự án quản lý công việc"},
    {"id": "Ticket", "label": "Ticket (NM-07)", "group": "workflow", "color": "#34d399", "desc": "Công việc / Issue / Nhiệm vụ"},
    {"id": "Sprint", "label": "Sprint (NM-08)", "group": "workflow", "color": "#6ee7b7", "desc": "Giai đoạn chạy sprint"},
    {"id": "KanbanColumn", "label": "KanbanColumn (NM-09)", "group": "workflow", "color": "#a7f3d0", "desc": "Cột trạng thái kanban"},
    {"id": "ApprovalRequest", "label": "ApprovalRequest (NM-10)", "group": "approval", "color": "#f59e0b", "desc": "Đơn từ đề xuất phê duyệt"},
    {"id": "ApprovalStep", "label": "ApprovalStep (NM-11)", "group": "approval", "color": "#fbbf24", "desc": "Bước duyệt trong quy trình"},
    {"id": "ScheduleEvent", "label": "ScheduleEvent (NM-12)", "group": "collab", "color": "#ec4899", "desc": "Sự kiện lịch họp / công tác"},
    {"id": "ScheduleRoom", "label": "ScheduleRoom (NM-13)", "group": "collab", "color": "#f472b6", "desc": "Phòng họp đặt trước"},
    {"id": "Notice", "label": "Notice (NM-14)", "group": "collab", "color": "#8b5cf6", "desc": "Bảng tin thông báo toàn công ty"},
    {"id": "Post", "label": "Post (NM-15)", "group": "collab", "color": "#a78bfa", "desc": "Bài viết diễn đàn nội bộ (Talk)"},
    {"id": "Asset", "label": "Asset (NM-16)", "group": "asset", "color": "#ef4444", "desc": "Tài sản thiết bị (Laptop, Server, v.v.)"},
    {"id": "AssetCategory", "label": "AssetCategory (NM-17)", "group": "asset", "color": "#f87171", "desc": "Danh mục phân loại tài sản"},
    {"id": "FileMetadata", "label": "FileMetadata (NM-18)", "group": "asset", "color": "#fca5a5", "desc": "Tệp đính kèm / File lưu trữ"},
    {"id": "ChatConversation", "label": "ChatConversation (NM-19)", "group": "collab", "color": "#c084fc", "desc": "Topology kênh chat (ChatMessage Option A)"},
    {"id": "Audience", "label": "Audience (NM-20)", "group": "collab", "color": "#d8b4fe", "desc": "Tập đối tượng người nhận thông báo"},
    {"id": "LeaveBalance", "label": "LeaveBalance (NM-21)", "group": "hr", "color": "#06b6d4", "desc": "Số dư phép năm lịch sử"},
    {"id": "AttendanceRecord", "label": "AttendanceRecord (NM-22)", "group": "hr", "color": "#22d3ee", "desc": "Dữ liệu chấm công hàng ngày"},
    {"id": "ContractHistory", "label": "ContractHistory (NM-23)", "group": "hr", "color": "#67e8f9", "desc": "Hợp đồng lao động nhân sự"},
    {"id": "Tag", "label": "Tag (NM-24)", "group": "workflow", "color": "#cbd5e1", "desc": "Thẻ phân loại ngữ nghĩa"}
]

# Canonical 43 Relationships (Ontology Edges)
ONTOLOGY_EDGES = [
    {"from": "User", "to": "Tenant", "label": "BELONGS_TO (RM-01)"},
    {"from": "Department", "to": "Tenant", "label": "BELONGS_TO (RM-02)"},
    {"from": "Department", "to": "Department", "label": "PARENT_OF (RM-03)"},
    {"from": "User", "to": "Department", "label": "MEMBER_OF (RM-04)"},
    {"from": "User", "to": "Role", "label": "HAS_ROLE (RM-05)"},
    {"from": "Role", "to": "Permission", "label": "HAS_PERMISSION (RM-06)"},
    {"from": "Project", "to": "Tenant", "label": "BELONGS_TO (RM-07)"},
    {"from": "User", "to": "Project", "label": "MEMBER_OF (RM-08)"},
    {"from": "Ticket", "to": "Project", "label": "PART_OF (RM-09)"},
    {"from": "Ticket", "to": "User", "label": "ASSIGNED_TO (RM-10)"},
    {"from": "Ticket", "to": "Sprint", "label": "IN_SPRINT (RM-11)"},
    {"from": "Ticket", "to": "KanbanColumn", "label": "IN_COLUMN (RM-12)"},
    {"from": "ApprovalRequest", "to": "Tenant", "label": "BELONGS_TO (RM-13)"},
    {"from": "ApprovalRequest", "to": "User", "label": "REQUESTED_BY (RM-14)"},
    {"from": "ApprovalRequest", "to": "ApprovalStep", "label": "HAS_STEP (RM-15)"},
    {"from": "ApprovalStep", "to": "User", "label": "ASSIGNED_APPROVER (RM-16)"},
    {"from": "ScheduleEvent", "to": "User", "label": "ORGANIZED_BY (RM-17)"},
    {"from": "ScheduleEvent", "to": "ScheduleRoom", "label": "LOCATED_IN (RM-18)"},
    {"from": "User", "to": "ScheduleEvent", "label": "ATTENDS (RM-19)"},
    {"from": "Notice", "to": "Tenant", "label": "BELONGS_TO (RM-20)"},
    {"from": "Notice", "to": "User", "label": "CREATED_BY (RM-21)"},
    {"from": "Notice", "to": "Audience", "label": "TARGETS (RM-22)"},
    {"from": "Audience", "to": "Department", "label": "INCLUDES_DEPT (RM-23)"},
    {"from": "Audience", "to": "User", "label": "INCLUDES_USER (RM-24)"},
    {"from": "Post", "to": "User", "label": "AUTHORED_BY (RM-25)"},
    {"from": "Post", "to": "Department", "label": "TARGETED_TO (RM-26)"},
    {"from": "ChatConversation", "to": "Tenant", "label": "BELONGS_TO (RM-27)"},
    {"from": "User", "to": "ChatConversation", "label": "PARTICIPATES_IN (RM-28)"},
    {"from": "FileMetadata", "to": "User", "label": "UPLOADED_BY (RM-29)"},
    {"from": "Asset", "to": "User", "label": "ASSIGNED_TO (RM-30)"},
    {"from": "Asset", "to": "Department", "label": "LOCATED_IN (RM-31)"},
    {"from": "Asset", "to": "AssetCategory", "label": "CATEGORIZED_AS (RM-32)"},
    {"from": "Asset", "to": "Tenant", "label": "BELONGS_TO (RM-33)"},
    {"from": "LeaveBalance", "to": "User", "label": "ACCRUED_FOR (RM-34)"},
    {"from": "LeaveBalance", "to": "Tenant", "label": "BELONGS_TO (RM-35)"},
    {"from": "AttendanceRecord", "to": "User", "label": "RECORDED_FOR (RM-36)"},
    {"from": "AttendanceRecord", "to": "Tenant", "label": "BELONGS_TO (RM-37)"},
    {"from": "ContractHistory", "to": "User", "label": "CONTRACT_FOR (RM-38)"},
    {"from": "ContractHistory", "to": "Tenant", "label": "BELONGS_TO (RM-39)"},
    {"from": "Tag", "to": "Project", "label": "TAGGED_TO (RM-40)"},
    {"from": "Tag", "to": "Post", "label": "TAGGED_TO (RM-41)"},
    {"from": "FileMetadata", "to": "Project", "label": "ATTACHED_TO (RM-42)"},
    {"from": "FileMetadata", "to": "Asset", "label": "ATTACHED_TO (RM-43)"}
]

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Groupware AI Chatbot - Graph Ontology & Data Visualizer</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        :root {
            --bg-color: #0f172a;
            --panel-bg: #1e293b;
            --text-color: #f8fafc;
            --accent-color: #38bdf8;
            --border-color: #334155;
        }
        body, html {
            margin: 0; padding: 0; width: 100%; height: 100%;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-color); color: var(--text-color); overflow: hidden;
        }
        #container { display: flex; width: 100%; height: 100%; }
        #sidebar {
            width: 360px; background-color: var(--panel-bg); border-right: 1px solid var(--border-color);
            display: flex; flex-direction: column; box-shadow: 2px 0 10px rgba(0,0,0,0.4); z-index: 10;
        }
        #sidebar-header { padding: 18px 20px; border-bottom: 1px solid var(--border-color); }
        #sidebar-header h2 { margin: 0 0 6px 0; font-size: 18px; color: var(--accent-color); }
        #sidebar-header p { margin: 0; font-size: 12px; color: #94a3b8; }
        #controls { padding: 15px 20px; border-bottom: 1px solid var(--border-color); }
        .control-group { margin-bottom: 12px; }
        .control-group label { display: block; font-size: 12px; font-weight: 600; text-transform: uppercase; margin-bottom: 6px; color: #cbd5e1; }
        .btn-group { display: flex; gap: 8px; }
        button, select, input {
            width: 100%; padding: 8px 12px; background: #0f172a; color: #f8fafc;
            border: 1px solid var(--border-color); border-radius: 6px; font-size: 13px; cursor: pointer; outline: none;
        }
        button.active { background: #0284c7; border-color: #38bdf8; font-weight: 600; }
        button:hover { background: #1e293b; }
        button.active:hover { background: #0284c7; }
        #sidebar-content { padding: 15px 20px; overflow-y: auto; flex: 1; }
        .stat-badge {
            display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px;
            font-weight: 600; margin-right: 6px; margin-bottom: 6px; background: #334155;
        }
        #details-panel {
            background: #0f172a; border-radius: 6px; padding: 12px; border: 1px solid var(--border-color);
            font-size: 13px; line-height: 1.5; word-break: break-all;
        }
        #graph-view { flex: 1; height: 100%; position: relative; }
        #network { width: 100%; height: 100%; }
        .legend {
            position: absolute; bottom: 20px; right: 20px; background: rgba(30, 41, 59, 0.9);
            padding: 12px 16px; border-radius: 8px; border: 1px solid var(--border-color);
            font-size: 12px; display: flex; flex-direction: column; gap: 6px; pointer-events: none;
        }
        .legend-item { display: flex; align-items: center; gap: 8px; }
        .legend-dot { width: 12px; height: 12px; border-radius: 50%; }
    </style>
</head>
<body>
    <div id="container">
        <div id="sidebar">
            <div id="sidebar-header">
                <h2>Groupware AI Chatbot</h2>
                <p>Architecture B: Operational Graph + Semantic Knowledge Graph</p>
            </div>
            <div id="controls">
                <div class="control-group">
                    <label>Chế độ hiển thị (View Mode)</label>
                    <div class="btn-group">
                        <button id="btn-ontology" class="active" onclick="switchMode('ontology')">1. Ontology Schema</button>
                        <button id="btn-instance" onclick="switchMode('instance')">2. Live Graph Data</button>
                    </div>
                </div>
                <div class="control-group" id="tenant-filter-group" style="display: none;">
                    <label>Lọc theo Tenant (Multi-Tenant)</label>
                    <select id="tenant-select" onchange="filterTenant()">
                        <option value="all">Toàn bộ Tenant (All Tenants)</option>
                        <option value="1">Tenant 1 (Công ty Công nghệ AI)</option>
                        <option value="2">Tenant 2 (Công ty Tài chính ERP)</option>
                    </select>
                </div>
                <div class="control-group">
                    <label>Tìm kiếm Node</label>
                    <input type="text" id="search-input" placeholder="Nhập tên node, email, serial..." oninput="searchNode()">
                </div>
            </div>
            <div id="sidebar-content">
                <div class="control-group">
                    <label>Thống kê hiện tại</label>
                    <div id="stats-area"></div>
                </div>
                <div class="control-group">
                    <label>Chi tiết Node được chọn (Inspector)</label>
                    <div id="details-panel">
                        <em>Nhấp vào bất kỳ Node hoặc Edge nào trên đồ thị để xem thuộc tính chi tiết.</em>
                    </div>
                </div>
            </div>
        </div>
        <div id="graph-view">
            <div id="network"></div>
            <div class="legend" id="legend">
                <div style="font-weight: bold; margin-bottom: 4px; color: #94a3b8;">PHÂN VÙNG KIẾN TRÚC</div>
                <div class="legend-item"><div class="legend-dot" style="background: #3b82f6;"></div> Tổ chức & Nhân sự (Org/User)</div>
                <div class="legend-item"><div class="legend-dot" style="background: #ef4444;"></div> Tài sản & Thiết bị (Asset/IT)</div>
                <div class="legend-item"><div class="legend-dot" style="background: #10b981;"></div> Dự án & Công việc (Workflow)</div>
                <div class="legend-item"><div class="legend-dot" style="background: #f59e0b;"></div> Phê duyệt (Approval)</div>
                <div class="legend-item"><div class="legend-dot" style="background: #8b5cf6;"></div> Truyền thông & Kênh chat (Collab)</div>
                <div class="legend-item"><div class="legend-dot" style="background: #06b6d4;"></div> Chấm công & Phép năm (HR)</div>
            </div>
        </div>
    </div>

    <script type="text/javascript">
        const ONTOLOGY_NODES = DATA_ONTOLOGY_NODES;
        const ONTOLOGY_EDGES = DATA_ONTOLOGY_EDGES;
        const INSTANCE_DATA = DATA_INSTANCE_DATA;

        let currentMode = 'ontology';
        let network = null;
        let allInstanceNodes = [];
        let allInstanceEdges = [];

        function initInstanceData() {
            const rawNodes = INSTANCE_DATA.nodes || {};
            const rawEdges = INSTANCE_DATA.relationships || [];

            const colorMap = {
                'Tenant': '#2563eb',
                'User': '#3b82f6',
                'Department': '#60a5fa',
                'Asset': '#ef4444',
                'AssetCategory': '#f87171',
                'ChatConversation': '#c084fc',
                'Notice': '#8b5cf6',
                'Audience': '#d8b4fe',
                'Project': '#10b981',
                'ApprovalRequest': '#f59e0b'
            };

            allInstanceNodes = [];
            for (const [label, items] of Object.entries(rawNodes)) {
                for (const it of items) {
                    const titleText = it.name || it.username || it.title || it.asset_code || `${label} #${it.id}`;
                    allInstanceNodes.push({
                        id: `${label}_${it.id}`,
                        label: `${label}: ${titleText}`,
                        group: label,
                        color: colorMap[label] || '#94a3b8',
                        shape: label === 'Tenant' ? 'hexagon' : (label === 'User' ? 'circle' : 'box'),
                        size: label === 'Tenant' ? 30 : 20,
                        tenant_id: it.tenant_id,
                        properties: it
                    });
                }
            }

            allInstanceEdges = rawEdges.map((rel, idx) => ({
                id: `rel_${idx}`,
                from: `${rel.source_label}_${rel.source_id}`,
                to: `${rel.target_label}_${rel.target_id}`,
                label: rel.rel_type,
                font: { size: 10, color: '#94a3b8', strokeWidth: 0 },
                arrows: 'to',
                color: { color: '#475569', highlight: '#38bdf8' },
                tenant_id: rel.tenant_id,
                properties: rel
            }));
        }

        function renderNetwork(nodesArray, edgesArray) {
            const container = document.getElementById('network');
            const data = {
                nodes: new vis.DataSet(nodesArray),
                edges: new vis.DataSet(edgesArray)
            };
            const options = {
                physics: {
                    solver: 'forceAtlas2Based',
                    forceAtlas2Based: {
                        gravitationalConstant: -50,
                        centralGravity: 0.01,
                        springLength: 120,
                        springConstant: 0.08
                    },
                    maxVelocity: 50,
                    stabilization: { iterations: 150 }
                },
                nodes: {
                    font: { color: '#f8fafc', size: 12, face: 'Arial' },
                    borderWidth: 2,
                    shadow: true
                },
                edges: {
                    smooth: { type: 'continuous' }
                },
                interaction: { hover: true, tooltipDelay: 200 }
            };

            if (network) network.destroy();
            network = new vis.Network(container, data, options);

            network.on('click', function(params) {
                if (params.nodes.length > 0) {
                    const nodeId = params.nodes[0];
                    const selected = nodesArray.find(n => n.id === nodeId);
                    displayDetails('Node: ' + (selected.label || selected.id), selected.properties || selected);
                } else if (params.edges.length > 0) {
                    const edgeId = params.edges[0];
                    const selected = edgesArray.find(e => e.id === edgeId);
                    displayDetails('Relationship: ' + (selected.label || ''), selected.properties || selected);
                }
            });
        }

        function displayDetails(title, dataObj) {
            const panel = document.getElementById('details-panel');
            let html = `<strong>${title}</strong><hr style="border-color: #334155; margin: 8px 0;">`;
            html += '<table style="width: 100%; border-collapse: collapse;">';
            for (const [k, v] of Object.entries(dataObj)) {
                if (k === 'properties' || k === 'color') continue;
                html += `<tr><td style="color: #94a3b8; padding: 3px 0; width: 40%; font-size: 11px;">${k}:</td>`;
                html += `<td style="color: #38bdf8; padding: 3px 0; font-size: 12px; font-weight: 500;">${JSON.stringify(v)}</td></tr>`;
            }
            html += '</table>';
            panel.innerHTML = html;
        }

        function switchMode(mode) {
            currentMode = mode;
            document.getElementById('btn-ontology').className = mode === 'ontology' ? 'active' : '';
            document.getElementById('btn-instance').className = mode === 'instance' ? 'active' : '';
            const tenantFilter = document.getElementById('tenant-filter-group');

            if (mode === 'ontology') {
                tenantFilter.style.display = 'none';
                updateStats(ONTOLOGY_NODES.length, ONTOLOGY_EDGES.length, 'Ontology Classes', 'Relationships');
                renderNetwork(
                    ONTOLOGY_NODES.map(n => ({
                        ...n,
                        shape: 'box',
                        margin: 10,
                        font: { color: '#ffffff', bold: true }
                    })),
                    ONTOLOGY_EDGES.map((e, idx) => ({
                        id: `onto_rel_${idx}`,
                        from: e.from,
                        to: e.to,
                        label: e.label,
                        arrows: 'to',
                        font: { size: 10, color: '#94a3b8' },
                        color: { color: '#64748b' }
                    }))
                );
            } else {
                tenantFilter.style.display = 'block';
                filterTenant();
            }
        }

        function filterTenant() {
            const val = document.getElementById('tenant-select').value;
            let filteredNodes = allInstanceNodes;
            let filteredEdges = allInstanceEdges;

            if (val !== 'all') {
                const tId = parseInt(val);
                filteredNodes = allInstanceNodes.filter(n => n.tenant_id === tId || n.tenant_id === undefined);
                const nodeIds = new Set(filteredNodes.map(n => n.id));
                filteredEdges = allInstanceEdges.filter(e => nodeIds.has(e.from) && nodeIds.has(e.to));
            }

            updateStats(filteredNodes.length, filteredEdges.length, 'Graph Nodes', 'Relationships');
            renderNetwork(filteredNodes, filteredEdges);
        }

        function updateStats(nLen, eLen, nName, eName) {
            const stats = document.getElementById('stats-area');
            stats.innerHTML = `
                <span class="stat-badge" style="background: #0284c7;">${nLen} ${nName}</span>
                <span class="stat-badge" style="background: #059669;">${eLen} ${eName}</span>
            `;
        }

        function searchNode() {
            const q = document.getElementById('search-input').value.toLowerCase().trim();
            if (!q || !network) return;
            const nodes = currentMode === 'ontology' ? ONTOLOGY_NODES : allInstanceNodes;
            const match = nodes.find(n => (n.label || '').toLowerCase().includes(q) || JSON.stringify(n).toLowerCase().includes(q));
            if (match) {
                network.focus(match.id, { scale: 1.5, animation: { duration: 600 } });
                network.selectNodes([match.id]);
                displayDetails(match.label || match.id, match.properties || match);
            }
        }

        // Initialize on load
        initInstanceData();
        switchMode('ontology');
    </script>
</body>
</html>
"""

class GraphVisualizer:
    def __init__(self):
        self.output_file = config.graph_export_dir / "graph_visualizer.html"
        self.snapshot_file = config.graph_export_dir / "graph_snapshot.json"

    def generate(self, auto_open: bool = True) -> Path:
        """Generates the interactive HTML visualization file."""
        if not self.snapshot_file.exists():
            from etl.pipeline import ETLPipeline
            logger.info("Graph snapshot not found. Running ETL pipeline to generate snapshot...")
            ETLPipeline().run(target="graph")

        with open(self.snapshot_file, "r", encoding="utf-8") as f:
            instance_data = json.load(f)

        html_content = HTML_TEMPLATE.replace(
            "DATA_ONTOLOGY_NODES", json.dumps(ONTOLOGY_NODES)
        ).replace(
            "DATA_ONTOLOGY_EDGES", json.dumps(ONTOLOGY_EDGES)
        ).replace(
            "DATA_INSTANCE_DATA", json.dumps(instance_data)
        )

        config.graph_export_dir.mkdir(parents=True, exist_ok=True)
        with open(self.output_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"Interactive graph visualizer generated at: {self.output_file}")

        if auto_open:
            webbrowser.open(f"file:///{self.output_file.resolve().as_posix()}")

        return self.output_file
