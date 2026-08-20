from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    XPreformatted,
)


ROOT = Path("/Users/shashi/Projects/Personal/infra-pilot")
OUT = ROOT / "output/pdf/InfraPilot_Interview_Preparation_Guide.pdf"
OUT.parent.mkdir(parents=True, exist_ok=True)


def register_fonts():
    regular = Path("/System/Library/Fonts/Supplemental/Arial.ttf")
    bold = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")
    italic = Path("/System/Library/Fonts/Supplemental/Arial Italic.ttf")
    if regular.exists() and bold.exists():
        pdfmetrics.registerFont(TTFont("Guide", str(regular)))
        pdfmetrics.registerFont(TTFont("Guide-Bold", str(bold)))
        if italic.exists():
            pdfmetrics.registerFont(TTFont("Guide-Italic", str(italic)))
        return "Guide", "Guide-Bold", "Guide-Italic" if italic.exists() else "Guide"
    return "Helvetica", "Helvetica-Bold", "Helvetica-Oblique"


FONT, BOLD, ITALIC = register_fonts()
NAVY = colors.HexColor("#0B1F33")
BLUE = colors.HexColor("#176B87")
CYAN = colors.HexColor("#19A7CE")
PALE = colors.HexColor("#EAF7FA")
INK = colors.HexColor("#17212B")
MUTED = colors.HexColor("#566575")
GREEN = colors.HexColor("#138A72")
AMBER = colors.HexColor("#A85D00")
RED = colors.HexColor("#B42318")
LIGHT = colors.HexColor("#F5F7FA")
LINE = colors.HexColor("#D7E0E8")


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="CoverTitle", fontName=BOLD, fontSize=28, leading=32, textColor=colors.white, alignment=TA_LEFT, spaceAfter=10))
styles.add(ParagraphStyle(name="CoverSub", fontName=FONT, fontSize=12, leading=17, textColor=colors.HexColor("#D7F2F7"), spaceAfter=8))
styles.add(ParagraphStyle(name="Section", fontName=BOLD, fontSize=20, leading=24, textColor=NAVY, spaceBefore=5, spaceAfter=12))
styles.add(ParagraphStyle(name="H2x", fontName=BOLD, fontSize=14, leading=18, textColor=BLUE, spaceBefore=12, spaceAfter=6))
styles.add(ParagraphStyle(name="H3x", fontName=BOLD, fontSize=11.2, leading=14, textColor=INK, spaceBefore=8, spaceAfter=4))
styles.add(ParagraphStyle(name="Bodyx", fontName=FONT, fontSize=9.25, leading=13, textColor=INK, spaceAfter=6))
styles.add(ParagraphStyle(name="Small", fontName=FONT, fontSize=7.8, leading=10.4, textColor=MUTED, spaceAfter=3))
styles.add(ParagraphStyle(name="Bulletx", fontName=FONT, fontSize=9.1, leading=12.7, textColor=INK, leftIndent=12, firstLineIndent=-8, bulletIndent=2, spaceAfter=3))
styles.add(ParagraphStyle(name="Q", fontName=BOLD, fontSize=10.1, leading=13.2, textColor=NAVY, spaceBefore=7, spaceAfter=3))
styles.add(ParagraphStyle(name="A", fontName=FONT, fontSize=9.05, leading=12.7, textColor=INK, leftIndent=8, borderColor=LINE, borderWidth=0.6, borderPadding=6, backColor=colors.white, spaceAfter=7))
styles.add(ParagraphStyle(name="Callout", fontName=FONT, fontSize=9.1, leading=12.7, textColor=INK, leftIndent=8, rightIndent=8, borderColor=CYAN, borderWidth=1, borderPadding=8, backColor=PALE, spaceBefore=5, spaceAfter=8))
styles.add(ParagraphStyle(name="Codex", fontName="Courier", fontSize=7.7, leading=10.2, textColor=INK, leftIndent=7, rightIndent=7, borderColor=LINE, borderWidth=0.5, borderPadding=7, backColor=LIGHT, spaceBefore=4, spaceAfter=7))
styles.add(ParagraphStyle(name="TOC", fontName=FONT, fontSize=10, leading=15, textColor=INK, leftIndent=8, spaceAfter=3))


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def p(text, style="Bodyx"):
    return Paragraph(text, styles[style])


def code_block(text):
    return XPreformatted(esc(text), styles["Codex"])


def bullets(items):
    return [Paragraph("- " + item, styles["Bulletx"]) for item in items]


def concept(title, what, why, when, points=None, project=None):
    out = [p(title, "H3x")]
    rows = [
        [p("WHAT", "Small"), p(what, "Bodyx")],
        [p("WHY", "Small"), p(why, "Bodyx")],
        [p("WHEN", "Small"), p(when, "Bodyx")],
    ]
    t = Table(rows, colWidths=[17 * mm, 165 * mm])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (0, -1), PALE),
        ("BOX", (0, 0), (-1, -1), 0.5, LINE),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    out.append(t)
    if points:
        out.extend(bullets(points))
    if project:
        out.append(p("<b>InfraPilot connection:</b> " + project, "Callout"))
    return out


def qa(question, answer):
    return [p("Q. " + question, "Q"), p("<b>Answer:</b> " + answer, "A")]


def header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.5)
    canvas.line(16 * mm, 14 * mm, w - 16 * mm, 14 * mm)
    canvas.setFont(FONT, 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(16 * mm, 9.5 * mm, "InfraPilot Interview Preparation Guide")
    canvas.drawRightString(w - 16 * mm, 9.5 * mm, f"{doc.page}")
    canvas.restoreState()


class GuideDocTemplate(BaseDocTemplate):
    pass


doc = GuideDocTemplate(
    str(OUT), pagesize=A4,
    rightMargin=15 * mm, leftMargin=15 * mm, topMargin=16 * mm, bottomMargin=18 * mm,
    title="InfraPilot Interview Preparation Guide",
    author="Prepared for Shashi S Azad",
    subject="InfraPilot, LangGraph, LangChain, RAG, vector databases, pgvector, PostgreSQL, FastAPI, MCP, and Prometheus",
)
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=header_footer)])

story = []

# Cover
cover = Table([[Paragraph("INFRAPILOT", ParagraphStyle(name="eyebrow", fontName=BOLD, fontSize=10, textColor=CYAN, leading=12)),],
               [p("Interview Preparation Guide", "CoverTitle")],
               [p("Project deep dive + complete, relevant notes for LangGraph, LangChain, RAG, Vector Databases, pgvector, PostgreSQL, FastAPI, MCP, and Prometheus", "CoverSub")],
               [Spacer(1, 14 * mm)],
               [p("Designed for backend, platform, SRE, DevOps, and applied-AI interviews", "CoverSub")],
               [p("Includes architecture explanations, why/when trade-offs, code and query examples, failure modes, improvement plans, and 100 interview questions with model answers.", "CoverSub")]], colWidths=[180 * mm], rowHeights=[10 * mm, 27 * mm, 25 * mm, 15 * mm, 10 * mm, 30 * mm])
cover.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), NAVY),
    ("BOX", (0, 0), (-1, -1), 0, NAVY),
    ("LEFTPADDING", (0, 0), (-1, -1), 12 * mm),
    ("RIGHTPADDING", (0, 0), (-1, -1), 12 * mm),
    ("TOPPADDING", (0, 0), (-1, -1), 3 * mm),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 3 * mm),
]))
story += [Spacer(1, 22 * mm), cover, Spacer(1, 14 * mm), p("Prepared for project-focused technical interviews | August 2026", "Small"), PageBreak()]

story += [p("How to use this guide", "Section")]
story += [p("This handbook is deliberately organized around the way interviewers probe a project: first explain the system, then defend design choices, then discuss failure handling, scale, security, and improvements. Each technology chapter uses the same <b>what / why / when</b> structure so that your answer explains a decision rather than reciting a definition.")]
story += bullets([
    "First pass: learn the 30-second and two-minute project explanations and the end-to-end investigation flow.",
    "Second pass: study the nine technology chapters. Say each trade-off aloud and connect it to InfraPilot.",
    "Final pass: answer the question bank without looking. Keep answers structured as context, choice, trade-off, evidence, and next improvement.",
    "Never claim functionality that is not implemented. Distinguish current behavior, known limitation, and production improvement.",
])
story += [p("Contents", "H2x")]
for item in [
    "1. InfraPilot project narrative and architecture",
    "2. LangChain",
    "3. LangGraph",
    "4. Retrieval-Augmented Generation (RAG)",
    "5. Vector databases and similarity search",
    "6. pgvector",
    "7. PostgreSQL",
    "8. FastAPI",
    "9. Model Context Protocol (MCP)",
    "10. Prometheus and PromQL",
    "11. Cross-technology design scenarios",
    "12. InfraPilot interview question bank",
    "13. Rapid revision sheets and official references",
]:
    story.append(p(item, "TOC"))
story.append(PageBreak())

# Project chapter
story += [p("1. InfraPilot: project narrative and architecture", "Section")]
story += [p("<b>Resume title:</b> InfraPilot - Agentic Infrastructure Incident Response Platform")]
story += [p("<b>30-second pitch.</b> InfraPilot is an agentic incident-response platform that turns a reported infrastructure incident into an evidence-grounded investigation. A FastAPI control plane persists incidents and runs a LangGraph workflow. The agent uses MCP tools to collect Kubernetes and Prometheus evidence, augments that evidence with runbooks stored in PostgreSQL/pgvector and prior incident memory, produces a structured root-cause assessment, and places any remediation behind explicit human approval and an allow-listed executor.", "Callout")]
story += [p("The problem it solves", "H2x")]
story += bullets([
    "Operators normally jump among kubectl, logs, events, metrics, dashboards, and runbooks. This increases cognitive load and delays correlation.",
    "A general chatbot may sound confident without inspecting live infrastructure. InfraPilot forces evidence collection through typed tools and stores the evidence with the run.",
    "Unrestricted autonomous remediation is unsafe. InfraPilot separates proposal, approval, and execution, and the executor ignores model-generated shell commands.",
])
story += [p("End-to-end investigation flow", "H2x")]
flow_rows = [
    [p("Stage", "Small"), p("Responsibility", "Small"), p("Why it exists", "Small")],
    [p("Incident API"), p("Validate and persist title, description, service, severity, and status."), p("Creates a durable business record before agent execution.")],
    [p("Classify"), p("Structured LLM output assigns incident category and priority."), p("Constrains downstream planning and routing.")],
    [p("Plan"), p("Build investigation steps appropriate to the symptom and target."), p("Makes execution explicit and inspectable.")],
    [p("Retrieve"), p("Fetch runbook chunks plus selected historical incidents."), p("Adds operational knowledge that may not be in model weights.")],
    [p("Agent/tool loop"), p("The model selects MCP evidence tools; results return to graph state."), p("Allows adaptive evidence gathering with a bounded loop.")],
    [p("Analyze"), p("Produce facts, ranked causes, checks, summary, and confidence."), p("Separates observations from hypotheses.")],
    [p("Propose"), p("Create a structured remediation proposal."), p("Proposal is not authorization.")],
    [p("Approve/execute"), p("Human decision followed by an allow-listed Kubernetes action."), p("Preserves control, safety, and auditability.")],
]
t = Table(flow_rows, colWidths=[30 * mm, 91 * mm, 61 * mm], repeatRows=1)
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("GRID", (0, 0), (-1, -1), 0.45, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
    ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
]))
story += [t]
story += [p("Key implementation facts you should state accurately", "H2x")]
story += bullets([
    "Graph path: classify -> plan -> retrieve runbooks -> retrieve history -> agent -> tools -> collect evidence -> increment -> agent loop -> analyze -> propose remediation -> finalize.",
    "The tool loop is bounded to five iterations. A bound protects cost, latency, and availability, but it can reduce completeness; stopping quality should also consider evidence sufficiency.",
    "MCP evidence tools cover Kubernetes logs, pod health, deployment health, events, resource metrics, and Prometheus application metrics.",
    "Runbooks use semantic vector retrieval with Sentence Transformers and pgvector cosine distance. The current historical incident lookup is recent-record retrieval, not vector similarity search.",
    "The LLM proposes remediation, but the executor supports only the allow-listed RESTART_DEPLOYMENT action and calls the Kubernetes API. Displayed commands are not executed.",
    "Partial graph state is persisted while streaming graph updates, so failed investigations can retain classification, plan, retrieval results, evidence, and tool counts.",
    "The current system is a strong local demonstration, not a production-ready incident platform: authentication, tenant isolation, durable queuing, robust secret redaction, least-privilege cluster access, target allow-lists, and deeper observability remain roadmap work.",
])
story += [p("Architecture layers", "H2x")]
story += bullets([
    "Experience layer: Next.js dashboard for incidents, investigations, evidence, runbooks, service inventory, approvals, execution results, and reruns.",
    "Control plane: FastAPI endpoints, Pydantic contracts, application services, persistence, streaming responses, and remediation gates.",
    "Reasoning plane: LangGraph orchestration, structured model calls, tool selection, evidence normalization, RAG, analysis, and proposals.",
    "Integration plane: MCP client/server boundary and Kubernetes/Prometheus adapters.",
    "Data plane: PostgreSQL for incidents, runs, evidence, approvals, results, and knowledge; pgvector for embeddings.",
    "Observed environment: local Docker Compose and a kind Kubernetes cluster containing deliberately healthy or broken demo services.",
])

for q, a in [
    ("Why is this agentic rather than a fixed automation?", "A fixed pipeline always runs the same checks. InfraPilot lets the model select the next typed evidence tool from the current incident, retrieved knowledge, and previous observations, then loops until the cap. Deterministic graph nodes still control the outer lifecycle, so agency exists inside explicit boundaries."),
    ("What is the strongest engineering decision?", "The safety boundary: planning and proposing are separated from approval and execution. The executor maps a validated enum to trusted Kubernetes API logic and does not execute model-authored shell text. That limits the blast radius of hallucination or prompt injection."),
    ("What would you improve first for production?", "Move investigations to a durable worker queue with idempotency, leases, retries, cancellation, and resumability; add authentication/RBAC and tenant or cluster boundaries; use service accounts with minimal Kubernetes permissions; add redaction and audit integrity; then evaluate retrieval and diagnosis quality with a labeled incident set."),
]:
    story += qa(q, a)

# LangChain
story += [PageBreak(), p("2. LangChain", "Section")]
story += [p("LangChain is an application framework and integration layer for composing language models, prompts, messages, tools, retrievers, structured outputs, middleware, and agents. It is useful when an application needs interchangeable model/provider integrations and reusable AI components; it is not a replacement for application architecture, persistence, authorization, or deterministic business logic.")]
story += concept("Core abstraction: model + messages", "A chat model consumes an ordered conversation made of system, human, AI, and tool messages and returns an AI message. Provider packages adapt a common interface to different APIs.", "A common interface reduces provider lock-in and allows invoke, stream, batch, async, structured output, and tool binding to be composed consistently.", "Use it when model calls are part of a larger Python application and you need provider portability or reusable conventions.", ["System messages define stable behavior; user messages carry the request; tool messages return execution results with matching call identifiers.", "Model parameters such as temperature, maximum tokens, timeout, and retry policy affect determinism, cost, latency, and failure behavior.", "Keep secrets and provider configuration outside prompts and source control."], "InfraPilot separates a tool-capable model from structured-output models so tool selection and schema-constrained analysis can be tuned independently.")
story += concept("Prompts and prompt templates", "Templates combine instructions, variables, examples, retrieved context, and output constraints into messages.", "They make prompt construction repeatable and testable, and prevent ad hoc string concatenation across the codebase.", "Use templates when a prompt has stable structure and dynamic incident, evidence, or retrieval fields.", ["Prefer explicit sections and delimit untrusted context.", "Few-shot examples help when labels or output style are hard to describe.", "Version prompts and test them against a representative evaluation set."], "Classification, analysis, and remediation prompts should explicitly distinguish confirmed facts, hypotheses, and recommended checks.")
story += concept("Tools and tool calling", "A tool is a typed callable exposed to a model with a name, description, and argument schema. The model requests a call; application code validates and executes it; the result becomes a tool message.", "Tools connect reasoning to current data and controlled actions without letting the model directly execute arbitrary code.", "Use tools for APIs, databases, search, telemetry, and bounded actions whose inputs can be validated.", ["Tool descriptions are part of the control surface: make scope, required arguments, and non-capabilities precise.", "Validate arguments again in application code; never rely on model compliance.", "Return structured, concise evidence and explicit error types."], "InfraPilot exposes read-only operational checks through MCP-backed LangChain tools. Remediation is deliberately outside the normal tool loop.")
story += concept("Structured output", "The model output is parsed or constrained into a schema such as a Pydantic model, JSON Schema, dataclass, or typed dictionary.", "Schemas reduce ambiguous prose and make outputs storable, renderable, and enforceable by downstream code.", "Use it for classifications, plans, analyses, remediation proposals, API-facing data, and any result consumed programmatically.", ["Schema validation improves shape, not factual correctness.", "Use constrained enums and field descriptions; retry only bounded parse failures.", "Log raw provider errors without leaking prompts or secrets."], "InfraPilot persists structured classification, analysis, and remediation fields instead of treating the model answer as an opaque paragraph.")
story += concept("Runnables, composition, streaming, and async", "LangChain components implement common invocation patterns and can be composed into pipelines. Operations may be synchronous, asynchronous, batched, or streamed.", "A uniform execution interface simplifies composition and observability.", "Use streaming for progressive UX, async for I/O concurrency, and batching for independent high-volume requests.", ["Async does not make CPU work faster; it prevents blocking while awaiting network or database I/O.", "Backpressure, cancellation, timeouts, and partial failures still need application-level handling.", "A stream is not automatically durable; clients may disconnect and workers may crash."], "InfraPilot exposes SSE progress, but a production design should run the investigation in a durable job and treat SSE as a view over persisted events.")
story += concept("Agents and middleware", "An agent repeatedly asks a model what to do, optionally invokes tools, adds results to state, and continues until completion. Middleware can intercept model, tool, and lifecycle events.", "Agents handle tasks where the next step depends on observations. Middleware centralizes cross-cutting controls such as retries, redaction, limits, and logging.", "Use an agent when adaptive planning materially outperforms a known deterministic sequence. Use a chain or normal code for fixed workflows.", ["Define stop conditions, budgets, and permitted tools.", "Prefer deterministic nodes for authorization and state transitions.", "Trace model calls, tool arguments, latency, token use, and errors."], "InfraPilot uses a graph-controlled agent loop: the graph decides lifecycle stages and maximum iterations; the model decides which evidence tool to request.")
story += [p("LangChain pitfalls", "H2x")]
story += bullets(["Treating a framework abstraction as a security boundary.", "Using free-form output where the application expects a stable schema.", "Building an agent for a deterministic task, adding unnecessary cost and failure modes.", "Retrying non-idempotent tools without deduplication.", "Passing huge tool outputs into context without summarization, filtering, or token budgeting.", "Depending on provider-specific behavior while claiming portability."])
for q, a in [
    ("LangChain versus LangGraph?", "LangChain supplies model, tool, retriever, prompt, structured-output, and agent integrations. LangGraph is the lower-level orchestration runtime for explicit state, branching, cycles, persistence, interrupts, and durable workflows. InfraPilot uses LangChain-compatible components inside a LangGraph-controlled process."),
    ("Why not call the Groq API directly?", "Direct calls are valid for a small fixed feature. LangChain becomes valuable when the same application needs typed tools, multiple message types, structured output, retrievers, provider substitution, and shared tracing conventions. The trade-off is another abstraction layer that must be understood and version-pinned."),
    ("Does structured output prevent hallucination?", "No. It validates syntax and field shape. Factual grounding still depends on evidence quality, prompt constraints, citations, post-validation, and evaluation."),
    ("How do you make tool use reliable?", "Use narrow descriptions, typed schemas, application-side validation, timeouts, explicit error results, bounded retries, idempotency for writes, and traces. Separate read-only evidence tools from privileged actions."),
    ("When should you avoid an agent?", "Avoid one when the sequence is known, correctness must be deterministic, latency or cost is tightly bounded, or the available actions are too dangerous to delegate. A normal service workflow or explicit graph is easier to test and operate."),
]: story += qa(q, a)

# LangGraph
story += [PageBreak(), p("3. LangGraph", "Section")]
story += [p("LangGraph models long-running AI work as a directed stateful graph. Nodes perform work, edges select what runs next, and reducers define how node updates merge into shared state. Its value is control: cycles, branching, persistence, interrupts, streaming, and inspection are explicit rather than hidden inside one agent call.")]
story += concept("State", "A typed shared object containing inputs, accumulated messages, evidence, counters, outputs, and lifecycle metadata. Nodes normally return partial updates rather than mutating global variables.", "Explicit state makes behavior inspectable, serializable, testable, and resumable.", "Use graph state when multiple steps need shared context or when execution can branch, loop, pause, or resume.", ["Keep state minimal and serializable.", "Separate durable business records from ephemeral prompt text.", "Do not store secrets unless necessary and protected."], "InfraPilot state carries the incident, classification, plan, retrieved knowledge, messages, raw and normalized evidence, iteration count, analysis, and remediation proposal.")
story += concept("Nodes and edges", "A node is a function over state. Normal edges define sequence; conditional edges choose the next node from state; entry and terminal edges start and end the run.", "They make control flow visible and allow deterministic policy nodes to surround probabilistic model nodes.", "Use conditional edges for tool routing, retry policy, approvals, and evidence sufficiency.", ["Keep nodes cohesive and independently testable.", "Return explicit status updates and errors.", "Side-effecting nodes require idempotency because durable runtimes may replay work."], "After the agent node, a conditional route either invokes tools or proceeds to analysis. A counter and maximum iteration limit prevent an unbounded loop.")
story += concept("Reducers and concurrent updates", "A reducer defines how a new state value combines with the current one, such as append messages, merge dictionaries, or replace a scalar.", "Without explicit merge semantics, parallel branches or repeated nodes can overwrite accumulated information.", "Use reducers for append-only messages/evidence or any field updated by multiple graph steps.", ["Choose append versus replace deliberately.", "Avoid non-deterministic merge functions.", "Deduplicate external observations when replay is possible."], "Tool messages and evidence are accumulated across iterations while classification or final analysis fields replace earlier values.")
story += concept("Checkpointing and threads", "A checkpointer stores graph state at execution boundaries, often keyed by a thread identifier. It enables resume, time travel, failure recovery, and human-in-the-loop pauses.", "Long-running workflows should not lose all progress when a process restarts or a model provider fails.", "Use persistence when runs are valuable, can exceed a request lifetime, or require approvals and audit trails.", ["A graph checkpoint is not automatically the same as the application's canonical audit record.", "Plan schema migration and retention for persisted graph state.", "Use stable run and thread identifiers."], "InfraPilot currently persists application records and partial node updates. Native durable checkpointing plus a worker queue would strengthen resumability.")
story += concept("Interrupts and human-in-the-loop", "An interrupt pauses graph execution and returns a value for external review. Resuming supplies a decision and continues from the saved checkpoint.", "It creates a first-class approval boundary inside a durable workflow.", "Use it before privileged changes, expensive operations, or decisions requiring accountability.", ["Code before an interrupt may be replayed; keep it idempotent.", "Do not put approval only in a prompt.", "Record who decided, when, what scope, and the reviewed payload."], "InfraPilot implements approval as persisted API state outside the graph. A future design could express proposal -> interrupt -> decision -> executor as a durable subgraph.")
story += concept("Streaming", "A graph can emit state updates, values, model tokens, messages, or custom progress events while it runs.", "Streaming improves perceived latency and makes multi-step execution observable.", "Use it for investigation timelines and progressive UI, but persist important events independently.", ["Handle reconnects with event IDs or a replay endpoint.", "Do not equate stream delivery with exactly-once processing.", "Redact tool output before sending it to clients."], "InfraPilot exposes investigation progress using Server-Sent Events; production should replay persisted events after disconnect.")
story += [p("Durability and correctness checklist", "H2x")]
story += bullets(["Stable run identifier and idempotency key.", "Checkpoint after meaningful state transitions.", "Bounded retries with error classification and jitter.", "Idempotent or compensatable side effects.", "Timeout and cancellation propagation.", "Tool and model budgets.", "Persisted node events and terminal status.", "Resume semantics tested after process termination."])
for q, a in [
    ("Why use a graph instead of one large agent prompt?", "A graph exposes lifecycle stages, state, loops, failure points, and policy boundaries. Individual nodes can be tested and retried, and deterministic code can control what the model is allowed to decide. A single prompt is simpler but opaque and difficult to resume."),
    ("Why cap tool iterations?", "A cap prevents runaway cost, latency, rate-limit pressure, and circular tool use. The weakness is that a fixed cap does not measure investigation quality, so a production design should combine hard budgets with an evidence-sufficiency evaluator and a clear incomplete result."),
    ("What happens if a node fails?", "Classify the error as transient, permanent, validation, policy, or cancellation. Retry only safe transient work, persist the last completed state, mark the run accurately, and expose a resumable or rerun operation. Side effects must be idempotent."),
    ("How would you support parallel evidence gathering?", "Fan out independent read-only checks such as logs, events, health, and metrics, then join them using deterministic reducers. Bound concurrency, preserve per-tool errors, and ensure the model receives a normalized, deduplicated evidence set."),
    ("What is the difference between graph state and database state?", "Graph state is execution context optimized for orchestration; database state is the canonical product and audit record. They can overlap, but treating checkpoints as the only business database complicates queries, lifecycle management, and compatibility."),
    ("How do interrupts work safely?", "Persist a checkpoint, emit the exact review payload, stop execution, and resume only with an authenticated decision tied to the run and proposal version. Assume pre-interrupt code can replay and make it idempotent."),
]: story += qa(q, a)

# RAG
story += [PageBreak(), p("4. Retrieval-Augmented Generation (RAG)", "Section")]
story += [p("RAG retrieves external knowledge at request time and gives selected context to a model before or during generation. It addresses finite model context and stale training knowledge, but it does not guarantee correctness. A RAG system is an information-retrieval system plus a generation system, so both halves need evaluation.")]
story += concept("Ingestion", "Load sources, clean and normalize text, split it into retrievable units, add metadata, generate embeddings, and write chunks and vectors to an index.", "Retrieval quality depends on what was indexed, how chunks preserve meaning, and whether provenance is retained.", "Run ingestion when documents are created or changed; use versioning and incremental re-indexing in production.", ["Preserve title, source, section, version, service, environment, permissions, and timestamps as metadata.", "Hash content for deduplication and re-index detection.", "Treat documents as untrusted input and scan for secrets or prompt injection."], "InfraPilot ingests operational runbooks and stores chunk text, source metadata, and embeddings in PostgreSQL/pgvector.")
story += concept("Chunking", "Split documents into units small enough to retrieve and fit in context while preserving enough local meaning.", "Oversized chunks dilute relevance and waste tokens; tiny chunks lose context and produce fragmented answers.", "Start with structure-aware recursive splitting, then tune chunk size and overlap using evaluation data.", ["Prefer headings, paragraphs, procedures, and semantic boundaries over arbitrary characters.", "Overlap helps preserve boundary context but increases storage and duplicate results.", "Parent-child retrieval can return a precise child match with a larger parent context."], "Operational runbooks benefit from procedure- or heading-aware chunks because individual diagnostic steps should remain coherent.")
story += concept("Embeddings", "An embedding model maps text to a dense vector whose geometry approximates semantic relatedness.", "It allows retrieval by meaning rather than exact token overlap.", "Use embeddings for semantic text or multimodal similarity; keep lexical search for identifiers, error codes, and exact names.", ["Query and document embeddings must use a compatible model and dimension.", "Changing the embedding model normally requires re-embedding the corpus.", "Track model name, version, dimension, normalization, and preprocessing."], "InfraPilot uses Sentence Transformers to embed runbook chunks and incident queries.")
story += concept("Retrieval and ranking", "Generate the query representation, retrieve candidates, apply metadata filters, optionally combine lexical and vector scores, rerank, and return the best evidence with provenance.", "The top vector neighbors are not always the most useful or authorized context.", "Use hybrid retrieval for corpora containing both natural-language concepts and exact operational identifiers.", ["Tune top-k, score thresholds, filters, diversity, and reranking against labeled queries.", "Maximum Marginal Relevance can reduce redundant chunks.", "Rerankers improve precision but add latency and cost."], "InfraPilot currently performs top-three cosine runbook retrieval. Service and environment metadata filters would reduce irrelevant operational guidance.")
story += concept("Context construction and generation", "Format selected chunks, provenance, instructions, and the user task within a token budget, then ask the model to answer only from supported evidence and identify uncertainty.", "Even correct retrieval can be ignored, confused, or overridden by a weak prompt.", "Use citation mapping and clear evidence/hypothesis separation for high-stakes operational reasoning.", ["Do not blindly concatenate large chunks.", "Deduplicate and order context intentionally.", "Quote or reference source identifiers so claims can be audited.", "Protect system instructions from retrieved prompt injection."], "InfraPilot combines live evidence, runbooks, and incident memory, then asks for structured facts, possible causes, checks, summary, and confidence.")
story += concept("RAG architectures", "Two-step RAG always retrieves before generation; agentic RAG lets an agent decide when and what to retrieve; hybrid designs combine predictable retrieval with adaptive tools or validation.", "The architecture controls predictability, latency, cost, and flexibility.", "Use two-step for documentation Q&A, agentic retrieval for open-ended research, and hybrid approaches for domain workflows with both mandatory and optional context.", ["Two-step RAG has a known maximum number of retrieval and generation calls.", "Agentic RAG can recover from an initially poor query but needs budgets and observability.", "Retrieval should sometimes abstain when no relevant context exists."], "InfraPilot always retrieves runbooks and recent history before the adaptive evidence tool loop, so it is a hybrid workflow.")
story += [p("RAG evaluation", "H2x")]
story += bullets([
    "Retrieval metrics: Recall@k, Precision@k, Mean Reciprocal Rank, nDCG, and coverage. Create labeled queries with relevant chunk judgments.",
    "Generation metrics: factual correctness, faithfulness to retrieved context, answer relevance, citation correctness, completeness, and calibrated abstention.",
    "Operational metrics: ingestion freshness, index lag, empty retrieval rate, latency, token cost, duplicate rate, and access-control violations.",
    "End-to-end evaluation: replay known incidents and measure root-cause ranking, useful-check recall, unsupported claims, and operator acceptance.",
])
for q, a in [
    ("Why RAG instead of fine-tuning?", "RAG is better for frequently changing, attributable operational knowledge: update the index without retraining and show provenance. Fine-tuning is better for behavior, style, task format, or learned patterns. They are complementary."),
    ("How do you choose chunk size?", "Start from the document structure and model context, then tune with retrieval evaluation. Chunks must be large enough to retain a complete idea or procedure and small enough to avoid diluted embeddings and wasted tokens. Measure rather than assume."),
    ("Why can top-k retrieval fail?", "The query may be vague, embeddings may miss exact identifiers, chunks may be poor, the corpus may lack the answer, or nearest neighbors may be redundant. Use query rewriting, hybrid search, metadata filters, MMR, reranking, thresholds, and abstention."),
    ("How do you prevent stale runbooks?", "Store source versions and timestamps, run incremental ingestion on change, expose index health and last-indexed time, delete superseded chunks, and alert on ingestion failures. At answer time, prefer valid environment-specific versions."),
    ("Is InfraPilot historical memory vector RAG?", "Not currently. Runbooks use embedding similarity. Historical incidents are selected from recent completed records. I would call that retrieved memory, not semantic vector retrieval, and improve it with service/severity filters, similarity, outcome quality, and recency weighting."),
    ("How do you defend against RAG prompt injection?", "Treat retrieved text as data, delimit it, never let it override system policy, filter or flag suspicious instructions, enforce authorization before retrieval, restrict tools outside the prompt, and log provenance. The execution allow-list remains the true safety boundary."),
]: story += qa(q, a)

# Vector DB
story += [PageBreak(), p("5. Vector databases and similarity search", "Section")]
story += [p("A vector database stores embeddings and supports nearest-neighbor search plus operational capabilities such as metadata filtering, persistence, indexing, concurrency, replication, and lifecycle management. A vector is only a numerical representation; the database is the system that finds nearby vectors efficiently.")]
story += concept("Similarity metrics", "Cosine compares direction, dot product combines angle and magnitude, and Euclidean distance measures straight-line distance.", "The embedding model's training objective determines which metric is meaningful. Choosing the wrong operator can change rankings.", "Use the metric recommended by the embedding model and apply the corresponding database operator and index operator class.", ["Cosine similarity = 1 - cosine distance.", "For unit-normalized vectors, cosine and dot-product rankings are closely related.", "Distances are not calibrated probabilities; thresholds require empirical tuning."], "InfraPilot uses cosine distance for semantic runbook matching.")
story += concept("Exact nearest neighbor search", "Compare a query vector with every eligible row and sort by distance.", "It provides exact ranking and is simple, making it a reliable baseline.", "Use it for small datasets, strict recall requirements, or filtered subsets where scanning is affordable.", ["Cost grows roughly with number of rows times vector dimension.", "Use exact search to measure recall loss from ANN indexes.", "Filters may make exact search competitive for narrow partitions."])
story += concept("Approximate nearest neighbor (ANN)", "An index searches a subset or graph of candidates to trade perfect recall for lower latency.", "Scanning millions of high-dimensional vectors per query is expensive.", "Use ANN when exact search violates latency or throughput goals and modest recall loss is acceptable.", ["Benchmark recall@k and p95 latency together.", "Index build time, memory, insertion behavior, and filter interaction matter.", "ANN parameters can be tuned at build time and query time."])
story += concept("HNSW", "A multilayer proximity graph navigated from coarse to fine layers to find nearby vectors.", "It usually provides strong query performance and recall without a training phase.", "Use it for low-latency search when memory and build cost are acceptable and the corpus changes incrementally.", ["More graph connectivity and larger search breadth improve recall but use more memory or CPU.", "Builds are heavier than simple inverted-file indexes.", "Filtering can reduce returned matches; iterative scans or partitions may help."])
story += concept("IVF / IVFFlat", "Vectors are assigned to coarse clusters or lists; a query probes the nearest lists and searches candidates inside them.", "It reduces comparisons and uses less memory than graph indexes in many cases.", "Use it for sufficiently large, relatively stable datasets when you can train the index and tune list/probe counts.", ["Too few probes harms recall; too many approaches exact-search cost.", "The index should be built after representative data exists.", "Distribution shifts may require rebuilding or retuning."])
story += concept("Metadata filtering and multi-tenancy", "Combine vector similarity with structured predicates such as service, environment, document version, ownership, or authorization scope.", "Semantic closeness alone must not cross security or operational boundaries.", "Always apply access-control and tenant filters before returning results.", ["Filtering after retrieval can produce fewer than k valid results.", "Partitioning or filtered indexes can improve selective workloads.", "Never depend on the LLM to remove unauthorized chunks."])
story += [p("Vector database selection criteria", "H2x")]
story += bullets(["Corpus size and vector dimension.", "Required recall, p50/p95 latency, and query throughput.", "Update/delete frequency and freshness.", "Metadata filtering and transaction needs.", "Hybrid lexical search support.", "Backup, replication, monitoring, and operational expertise.", "Data residency and access control.", "Whether adding a separate system is justified versus extending the existing database."])
for q, a in [
    ("Is a vector database always required for RAG?", "No. Small corpora can use in-memory exact search; existing search engines can combine lexical and vector retrieval; structured data may be queried directly. Use a vector database when semantic retrieval and its operational requirements justify it."),
    ("Cosine distance versus cosine similarity?", "Similarity increases as vectors become closer; distance decreases. In pgvector, the cosine distance operator is <=>, so a similarity score can be written as 1 - distance. Keep ordering direction explicit."),
    ("How do you choose HNSW versus IVFFlat?", "Benchmark on representative data. HNSW often gives a better speed-recall trade-off and needs no training but uses more memory and builds more slowly. IVFFlat can build faster and use less memory, but needs representative data and careful list/probe tuning."),
    ("What is high cardinality in vector metadata?", "It means many distinct filter values, such as a tenant ID per customer. It affects index design, partitioning, cache locality, and query planning. Security predicates still come first even if they reduce ANN efficiency."),
    ("What is embedding drift?", "Changing the model, version, preprocessing, or domain distribution changes vector geometry. Store embedding metadata, avoid mixing incompatible vectors, run shadow evaluations, and re-embed with a migration plan."),
]: story += qa(q, a)

# pgvector
story += [PageBreak(), p("6. pgvector", "Section")]
story += [p("pgvector is a PostgreSQL extension that adds vector types, distance operators, exact nearest-neighbor search, and ANN indexes. It is compelling when relational metadata, transactions, joins, backups, and vectors belong in one operational system.")]
story += concept("Vector types and dimensions", "The vector column stores a fixed-dimensional dense embedding. pgvector also supports half-precision, sparse, and binary representations in supported versions.", "The database can validate dimensions and execute optimized distance operations.", "Use the representation that matches model output, precision needs, storage budget, and index support.", ["All values in a fixed vector column must match its declared dimension.", "Store the embedding model and version alongside the row or index version.", "Do not mix incompatible embedding spaces in the same retrieval query."], "Runbook chunks use a vector column aligned to the selected Sentence Transformer output dimension.")
story += concept("Distance operators", "pgvector exposes operators for L2 distance, inner product, cosine distance, and other supported distances.", "The ORDER BY operator determines both ranking and which ANN operator class can accelerate the query.", "Choose the operator recommended by the embedding model and build the matching index operator class.", ["L2: <->", "Negative inner product: <#>", "Cosine distance: <=>", "The query must use ORDER BY distance directly with LIMIT for index use."], "InfraPilot orders runbook chunks by cosine distance and limits the result set.")
story += concept("HNSW and IVFFlat indexes", "HNSW builds a proximity graph; IVFFlat partitions vectors into lists. Both approximate exact nearest-neighbor order.", "They reduce query latency at scale by searching fewer candidates.", "Add ANN only after measuring exact-search latency and recall needs.", ["Use vector_cosine_ops for cosine queries, vector_l2_ops for L2, and the matching class for other metrics.", "HNSW query breadth and IVFFlat probes trade latency for recall.", "Create indexes concurrently where operational requirements and extension support permit, and monitor build resources."])
story += concept("Relational filtering", "A vector query can include normal SQL predicates and joins for service, environment, permissions, status, or version.", "This is pgvector's major architectural advantage: semantic and relational constraints share one transaction and query planner.", "Use filters for authorization and relevance; consider B-tree indexes, partial indexes, partitions, or iterative scans for selective predicates.", ["ANN filtering may occur after candidate selection depending on plan and version.", "Inspect EXPLAIN ANALYZE rather than assuming the vector index is used.", "Increase candidate breadth only after measuring filtered recall."])
story += [p("Representative SQL", "H2x")]
story += [code_block("""CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE runbook_chunks (
  id bigserial PRIMARY KEY,
  source text NOT NULL,
  service text,
  content text NOT NULL,
  embedding vector(384) NOT NULL
);

CREATE INDEX runbook_embedding_hnsw
ON runbook_chunks USING hnsw (embedding vector_cosine_ops);

SELECT id, source, content,
       1 - (embedding <=> :query_vector) AS similarity
FROM runbook_chunks
WHERE service = :service
ORDER BY embedding <=> :query_vector
LIMIT 5;""")]
story += [p("Operational guidance", "H2x")]
story += bullets(["Keep ordinary indexes for structured filters; a vector index does not replace relational indexes.", "Benchmark exact versus ANN results and record recall@k.", "Use EXPLAIN (ANALYZE, BUFFERS) on representative queries.", "Plan VACUUM, autovacuum, backups, replication, and extension upgrades like any production PostgreSQL workload.", "Batch embedding writes and avoid holding long transactions.", "Separate or partition tenants when security, retention, or performance requires it."])
for q, a in [
    ("Why pgvector instead of a dedicated vector database?", "InfraPilot already needs PostgreSQL for incidents and investigations. pgvector keeps text, metadata, vectors, joins, transactions, migrations, and backups in one system, reducing operational complexity. A dedicated system may win at extreme scale or specialized search features."),
    ("Does an HNSW index guarantee exact results?", "No. It is approximate. Measure recall against exact search and tune search breadth. Correct SQL shape and matching operator class are also required for index use."),
    ("How do metadata filters affect ANN?", "A selective filter can leave too few valid candidates when filtering occurs around an approximate scan. Add relational indexes, tune candidate breadth, use iterative scans where available, partition, or run exact search on a small filtered subset."),
    ("How do you migrate embedding models?", "Add a new vector column or versioned table/index, backfill in batches, dual-read or shadow-query, compare retrieval metrics, switch traffic, and remove the old representation only after validation and rollback time."),
    ("How do you debug a slow pgvector query?", "Use EXPLAIN ANALYZE with buffers, verify ORDER BY distance plus LIMIT, confirm matching operator class, inspect filter selectivity, table statistics, index size, probes/search breadth, cache state, and connection saturation."),
]: story += qa(q, a)

# PostgreSQL
story += [PageBreak(), p("7. PostgreSQL", "Section")]
story += [p("PostgreSQL is InfraPilot's system of record. It stores transactional incident state and audit data while pgvector extends the same database for semantic retrieval. Interviewers will expect you to understand correctness and operations beyond basic CRUD.")]
story += concept("ACID transactions", "Atomicity commits all changes or none; consistency preserves declared invariants; isolation controls concurrent visibility; durability preserves committed data through failures under the configured guarantees.", "An investigation creates and updates related state that must not become internally contradictory.", "Use transactions around one logical state transition, but keep them short and avoid network/model calls inside them.", ["Database consistency is not the same as business correctness.", "External APIs require sagas, outbox patterns, or idempotent reconciliation rather than one cross-system ACID transaction.", "Handle serialization failures and deadlocks with bounded whole-transaction retries."], "Approval, execution status, and result transitions should be validated and persisted atomically.")
story += concept("MVCC", "Multi-Version Concurrency Control lets readers see a consistent snapshot while writers create new row versions.", "Readers and writers often avoid blocking each other, improving concurrency.", "Understand MVCC whenever concurrent requests read and update incidents or investigations.", ["Old row versions require VACUUM cleanup.", "Long-running transactions delay cleanup and can cause bloat.", "Visibility depends on isolation level and snapshot timing."])
story += concept("Isolation and locking", "PostgreSQL provides Read Committed, Repeatable Read, and Serializable behavior plus explicit row/table/advisory locks.", "Concurrent approval, rerun, and execute requests can otherwise cause invalid transitions or duplicate actions.", "Use row locking or conditional updates for state machines; use Serializable only where its cost and retry behavior are justified.", ["Read Committed is the default and each statement sees a fresh snapshot.", "SELECT ... FOR UPDATE locks selected rows for controlled transitions.", "Optimistic concurrency can update WHERE id = ? AND version = ? and detect zero affected rows."])
story += concept("Indexes", "Indexes maintain searchable structures such as B-tree, GIN, GiST, BRIN, or extension-specific ANN indexes.", "They reduce reads at the cost of storage, memory, write amplification, and maintenance.", "Index frequent selective filters, joins, uniqueness constraints, and orderings based on measured query plans.", ["Composite index column order matters.", "Partial indexes cover a predicate such as active rows.", "Unused indexes still cost writes.", "Use EXPLAIN ANALYZE and realistic data distribution."])
story += concept("JSONB versus normalized columns", "JSONB stores flexible structured values with operators and GIN indexing; normalized columns enforce stronger types, constraints, joins, and predictable queries.", "Agent evidence and model output can vary, while lifecycle fields have stable semantics.", "Use columns for identifiers, status, timestamps, joins, and frequently queried fields; JSONB for evolving evidence payloads with validation at boundaries.", ["Avoid turning the entire schema into unvalidated JSON.", "Index only queried JSON paths.", "Consider schema_version inside long-lived payloads."], "InfraPilot can store tool findings and structured model payloads in JSONB while keeping run IDs, statuses, approvals, timestamps, and relationships relational.")
story += concept("Connection pooling", "A pool reuses a bounded set of database connections across requests or workers.", "Opening a connection per request is expensive, while too many connections consume PostgreSQL memory and cause contention.", "Use an async-compatible pool with FastAPI and set pool size from total worker concurrency and database capacity.", ["Set connect, statement, and pool-acquisition timeouts.", "Measure pool wait time and saturation.", "Avoid sharing one transaction/session across unrelated async tasks."])
story += concept("Migrations and schema evolution", "Versioned migrations apply ordered changes and support coordinated application/database releases.", "Persistent investigation data outlives a single application version.", "Use migrations for every production schema change and test upgrade and rollback paths on realistic data.", ["Use expand-and-contract for zero-downtime changes.", "Backfill separately from fast DDL where necessary.", "Do not assume application and database deploy atomically."], "InfraPilot uses Alembic at backend startup in Compose; a production deployment should run migrations as a controlled job rather than every replica racing at startup.")
story += [p("Production operations", "H2x")]
story += bullets(["Monitor slow queries, locks, deadlocks, connections, cache hit rate, WAL, replication lag, table/index bloat, vacuum progress, and disk growth.", "Use point-in-time recovery with tested backups; a backup that has not been restored is an assumption.", "Set statement timeouts and separate roles with least privilege.", "Use unique constraints and foreign keys to make invariants real.", "Partition only when access, retention, or very large-table behavior justifies complexity."])
for q, a in [
    ("How do you prevent double remediation execution?", "Use an atomic state transition guarded by status and proposal version, for example UPDATE ... WHERE remediation_status='APPROVED' RETURNING. Add an idempotency key or unique execution record, execute through a worker, and reconcile uncertain external results."),
    ("Why not store everything in JSONB?", "Stable fields need constraints, indexes, joins, and discoverable schemas. JSONB is valuable for variable tool payloads, but overuse moves integrity into application code and makes analytics and migrations harder."),
    ("What causes deadlocks?", "Transactions acquire conflicting locks in different orders. PostgreSQL aborts one participant. Keep transactions short, lock objects in a consistent order, index predicates so updates touch fewer rows, and retry the entire transaction with jitter."),
    ("How would you model investigation evidence?", "Use an append-oriented evidence table keyed by run ID with tool, status, normalized finding JSONB, provenance, timestamps, sequence, and optional content hash. Keep run summary and lifecycle status in the investigation table."),
    ("What is EXPLAIN ANALYZE risk?", "It executes the query, so writes will happen and expensive queries can affect production. Use it carefully, preferably on replicas or staging, and add BUFFERS to see I/O behavior."),
]: story += qa(q, a)

# FastAPI
story += [PageBreak(), p("8. FastAPI", "Section")]
story += [p("FastAPI is an ASGI web framework built around Python type hints, Starlette, and Pydantic. It provides request parsing, validation, dependency injection, OpenAPI generation, and async support, but application correctness still depends on clean service boundaries and durable job design.")]
story += concept("ASGI and async I/O", "ASGI is an asynchronous server/application interface supporting HTTP, streaming, and long-lived connections. async def yields control while awaiting I/O.", "An API coordinating databases, LLM providers, MCP servers, and Kubernetes performs substantial network I/O.", "Use async endpoints and clients when dependencies are async. Offload CPU-bound work or blocking libraries rather than blocking the event loop.", ["Async improves concurrency, not per-operation speed.", "A blocking SDK inside async def can stall every request on that worker.", "Set timeouts and cancellation behavior for all outbound calls."], "InfraPilot should avoid keeping the main request open for a complete investigation; enqueue work and use status or SSE for progress.")
story += concept("Pydantic request and response models", "Typed models parse and validate external data and generate JSON Schema for OpenAPI.", "They create explicit API contracts and prevent malformed values from reaching business logic.", "Use separate create, update, list, detail, and internal models to control required fields and exposure.", ["Validation does not authorize a request.", "Use constrained enums and validators for state transitions.", "Set response models to avoid accidentally returning internal fields."])
story += concept("Dependency injection", "Dependencies declare reusable request-scoped requirements such as database sessions, authenticated users, settings, or services.", "It centralizes lifecycle and policy while keeping routes testable.", "Use dependencies for resource acquisition, authentication, authorization, and service composition; avoid hidden global state.", ["Dependencies can be async generators with cleanup.", "Override dependencies in tests.", "Do not put long business workflows directly in dependency functions."], "Database sessions and application services can be injected into incident and investigation routers.")
story += concept("Exception handling and status codes", "Domain errors are mapped to stable HTTP status codes and response bodies at the API boundary.", "Clients need to distinguish validation, absence, conflict, unauthorized access, rate limits, and server failure.", "Define centralized exception handlers and do not expose raw provider or Kubernetes exceptions.", ["400 malformed business request; 401 unauthenticated; 403 forbidden; 404 absent; 409 state conflict; 422 validation; 429 throttled; 5xx server/dependency failure.", "Include a safe error code and correlation ID.", "Log stack traces server-side with redaction."])
story += concept("Server-Sent Events (SSE)", "SSE is a one-way HTTP stream from server to browser using text/event-stream events with optional event names, IDs, and retry hints.", "It is simpler than WebSockets when the client only needs progress updates.", "Use SSE for investigation timelines; use WebSockets when the client must also send frequent messages over the same connection.", ["Support heartbeat events through proxies.", "Use event IDs and a replay endpoint for reconnects.", "Persist progress separately because a stream can disconnect."], "InfraPilot's investigation stream can expose node progress; the durable run record remains the source of truth.")
story += concept("BackgroundTasks versus a durable queue", "FastAPI BackgroundTasks runs work after returning a response in the same application process. A durable queue stores jobs for workers with retries, leases, and recovery.", "An agent investigation can outlive a request and must survive API restarts.", "Use BackgroundTasks for small non-critical same-process work. Use Celery, Dramatiq, Arq, RQ, or another durable system for valuable long-running jobs.", ["Do not promise durability from an in-process task.", "Define idempotent job handlers and observable attempts.", "Separate API scaling from worker scaling."], "A production InfraPilot should enqueue an investigation and return 202 Accepted with a run ID.")
story += concept("Security", "Authentication identifies the caller; authorization checks permitted actions and resources. Additional controls include CORS, CSRF where applicable, rate limiting, input limits, secret handling, and audit logging.", "Incident evidence and remediation capabilities are sensitive and privileged.", "Apply auth and scoped RBAC before exposing a control plane beyond a trusted local environment.", ["CORS is a browser policy, not authentication.", "Use short-lived credentials and least privilege.", "Never return kubeconfig, tokens, raw secrets, or unredacted logs."], "InfraPilot's present local configuration should be described as a demo boundary, with auth/RBAC and service-account-based access on the production roadmap.")
story += [p("Testing strategy", "H2x")]
story += bullets(["Unit-test services and graph nodes with deterministic model/tool fakes.", "API-test validation, status codes, conflicts, auth, and response models using an ASGI test client.", "Contract-test MCP tool names, schemas, error shapes, and timeouts.", "Integration-test PostgreSQL migrations and transaction behavior.", "End-to-end test create -> investigate -> evidence -> approve -> execute against an isolated cluster.", "Load-test concurrent SSE connections, queue throughput, database pools, and provider limits."])
for q, a in [
    ("Why does async not solve long-running investigations?", "Async frees a worker while awaiting I/O, but the request and process still own the workflow. Disconnects, deployments, timeouts, and crashes can lose progress. A durable queue/checkpointer solves lifecycle durability; SSE only reports progress."),
    ("Why return 202 Accepted?", "The server has accepted an asynchronous operation but not completed it. Return the run ID and status URL, then let clients poll or subscribe to progress. Final success or failure belongs to the job state, not the initial response."),
    ("How do you test SSE?", "Use a streaming test client, assert content type and event framing, consume named events incrementally, test terminal and error events, simulate disconnect/reconnect with Last-Event-ID, and verify event persistence separately."),
    ("How do you avoid leaking ORM objects?", "Use explicit response models, map database entities to API DTOs, disable accidental lazy loading during serialization, and keep internal fields out of response schemas."),
    ("What should a health endpoint check?", "Liveness should report whether the process can serve. Readiness should validate required dependencies with tight timeouts. Avoid making liveness depend on every external provider or Kubernetes API, which can cause restart storms."),
]: story += qa(q, a)

# MCP
story += [PageBreak(), p("9. Model Context Protocol (MCP)", "Section")]
story += [p("MCP is an open protocol for connecting AI applications to context and capabilities through a standardized client-server boundary. It uses JSON-RPC messages and capability negotiation. The host controls the overall application, clients maintain server connections, and servers expose primitives such as tools, resources, and prompts.")]
story += concept("Host, client, and server", "The host is the AI application; an MCP client inside it connects to one server; a server provides scoped capabilities or context.", "The separation makes integrations modular and lets the host enforce consent, routing, and policy.", "Use MCP when multiple AI hosts or agents should consume a stable integration contract rather than custom wrappers.", ["The host remains responsible for user control and security.", "A server should expose a narrow domain boundary.", "Server process isolation is useful but not sufficient authorization."], "InfraPilot's reasoning service acts as host/client and connects to an infrastructure MCP server that wraps Kubernetes and Prometheus access.")
story += concept("JSON-RPC and lifecycle", "MCP messages are JSON-RPC requests, responses, and notifications. Initialization negotiates protocol version and capabilities before normal operations.", "Explicit capabilities let implementations interoperate without assuming every feature exists.", "Handle initialize, capability checks, normal requests, cancellation, errors, and shutdown consistently.", ["Requests have IDs and expect responses; notifications do not.", "Validate protocol versions and schemas.", "Separate transport failures from tool-level failures."])
story += concept("Tools", "Model-controlled executable functions described by name, purpose, and input schema; results may contain text or structured content.", "Tools let the model request current data or bounded operations through an explicit contract.", "Use tools for dynamic queries or actions; keep dangerous operations behind approval and authorization.", ["Tool annotations and descriptions are hints, not enforcement.", "Validate and authorize every call server-side.", "Return explicit error information without exposing secrets."], "InfraPilot MCP tools are read-only evidence operations. Privileged remediation stays in a separate allow-listed executor.")
story += concept("Resources", "Application-controlled context identified by URIs, such as files, records, schemas, or documentation that clients can list or read.", "Resources represent inspectable context without pretending every read is an action.", "Use resources when the application or user selects context; use tools when a model must execute a parameterized operation.", ["Attach MIME types and provenance.", "Apply authorization to resource discovery and reads.", "Consider subscriptions only when clients can handle updates safely."])
story += concept("Prompts", "User-controlled reusable templates or workflows exposed by a server.", "They package domain-specific interaction patterns while leaving invocation under user or host control.", "Use prompts for discoverable workflows such as 'investigate deployment latency' rather than hidden policy enforcement.", ["Prompts are not trusted executable policy.", "Make arguments and resulting messages transparent.", "Version prompts when clients depend on stable behavior."])
story += concept("Transports", "Standard transports include local stdio and Streamable HTTP. Both carry UTF-8 JSON-RPC messages.", "Transport choice determines process lifecycle, network boundary, authentication, latency, and deployment complexity.", "Use stdio for local child-process integrations and Streamable HTTP for remote or shared services requiring network controls.", ["Never log protocol data to stdout in a stdio server; use stderr for logs.", "HTTP deployments need TLS, authorization, origin/security controls, timeouts, and session handling.", "Transport security does not replace tool authorization."], "InfraPilot can run its MCP integration locally for development; a production remote server should use authenticated HTTP and cluster-scoped identity.")
story += concept("Security and trust", "MCP enables data access and code execution, so consent, least privilege, authorization, audience-bound tokens, input validation, redaction, and audit logging are core controls.", "A compromised server, prompt injection, or overpowered credential can turn helpful tooling into a control-plane risk.", "Apply defense in depth for every server and every tool, especially infrastructure actions.", ["Do not pass upstream access tokens through to downstream services.", "Bind credentials to the intended server and scope.", "Treat tool results as untrusted data before placing them in prompts.", "Require human review for high-impact actions."], "InfraPilot's strongest boundary is keeping remediation out of MCP evidence tools and executing only a trusted action enum after approval.")
for q, a in [
    ("MCP versus a normal REST API?", "REST defines an application HTTP interface. MCP defines AI-oriented discovery and invocation semantics for tools, resources, and prompts over JSON-RPC transports. An MCP server can wrap REST APIs; MCP does not replace service APIs for ordinary consumers."),
    ("MCP versus LangChain tools?", "A LangChain tool is an in-process framework abstraction. MCP is a protocol boundary with discovery, schemas, lifecycle, and transports. An MCP client can adapt remote MCP tools into LangChain-compatible tools."),
    ("Why keep remediation outside the MCP tool loop?", "Evidence gathering is read-only and broadly safe; remediation changes infrastructure. Separation prevents the model from directly invoking privileged actions, allows a human decision and policy check, and narrows the executor's credentials and code path."),
    ("How do you version MCP tools?", "Prefer backward-compatible schema changes, capability discovery, clear deprecation, and contract tests. For breaking semantics, publish a new tool name or server version and migrate clients deliberately."),
    ("How do you handle tool timeouts?", "Set deadlines at client and server, propagate cancellation, return a typed timeout result, avoid blind retries of writes, record latency and attempt metadata, and let the graph decide whether alternative evidence can satisfy the task."),
]: story += qa(q, a)

# Prometheus
story += [PageBreak(), p("10. Prometheus and PromQL", "Section")]
story += [p("Prometheus is a pull-based monitoring system and time-series database. Targets expose metrics, Prometheus scrapes samples into labeled time series, PromQL evaluates them, and alerting or dashboards consume the results. It is optimized for numeric telemetry and dimensional queries, not raw logs or long-term event storage.")]
story += concept("Time series and labels", "A series is identified by a metric name plus its complete label set; samples are timestamped values.", "Labels allow aggregation and filtering across services, instances, routes, methods, and status classes.", "Use labels for bounded dimensions required by queries. Never use unbounded values such as request IDs or user IDs.", ["Every unique label combination creates another series.", "Cardinality drives memory, storage, and query cost.", "Use stable naming and base units such as seconds and bytes."], "Payment metrics label method, endpoint, and status so InfraPilot can calculate error rates and latency by route.")
story += concept("Counter", "A cumulative value that normally only increases, except when a process restarts.", "Counters accurately represent totals while PromQL derives rates over a time window and handles resets.", "Use for requests, errors, jobs, bytes, or events completed.", ["Query counters with rate() for per-second trends or increase() for approximate window totals.", "Do not use a counter for a value that can decrease.", "Apply rate before aggregation when resets may differ by instance."], "payment_http_requests_total supports success/error counts and 5xx ratios.")
story += concept("Gauge", "A value that can increase or decrease.", "It models current state rather than accumulated events.", "Use for queue depth, replicas, temperature, memory, or jobs in progress.", ["Functions such as avg_over_time, max_over_time, and deriv can describe gauge behavior.", "A gauge's value can become stale if the exporter stops; pair it with up and freshness checks."])
story += concept("Histogram", "A histogram counts observations in cumulative buckets and also emits count and sum series. Quantiles are calculated at query time from buckets.", "Histograms aggregate across instances and allow multiple quantiles from one distribution.", "Use for request duration or size when server-side aggregation and SLO analysis are required.", ["Choose buckets around meaningful SLO thresholds.", "Classic bucket series include an le label and are cumulative.", "For p95 across instances: histogram_quantile(0.95, sum by (le) (rate(metric_bucket[5m])))."], "payment_http_request_duration_seconds exposes bucket, count, and sum series used for p95 latency.")
story += concept("Summary", "A summary observes values and may calculate client-side quantiles plus count and sum.", "It can provide accurate process-local quantiles over a configured window.", "Use only when quantiles are known in advance and aggregation across instances is unnecessary.", ["Summary quantiles generally cannot be meaningfully averaged or aggregated across replicas.", "Count and sum still support average calculation.", "Histograms are usually more flexible for distributed services."])
story += concept("Scraping and service discovery", "Prometheus periodically discovers targets and pulls their exposition endpoints.", "Pulling centralizes collection health and makes missing targets visible through the up metric.", "Use service discovery and relabeling in Kubernetes; use Pushgateway only for suitable short-lived batch jobs, not as a general push replacement.", ["Scrape interval controls freshness and storage volume.", "A successful HTTP response can still contain invalid exposition data.", "Protect metrics endpoints if they reveal sensitive topology or data."])
story += [p("Essential PromQL", "H2x")]
story += [code_block("""# Request rate by service
sum by (service) (rate(http_requests_total[5m]))

# 5xx ratio
sum(rate(payment_http_requests_total{status=~"5.."}[5m]))
/
sum(rate(payment_http_requests_total[5m]))

# p95 latency from a classic histogram
histogram_quantile(
  0.95,
  sum by (le) (rate(payment_http_request_duration_seconds_bucket[5m]))
)

# Average latency
sum(rate(payment_http_request_duration_seconds_sum[5m]))
/
sum(rate(payment_http_request_duration_seconds_count[5m]))""")]
story += concept("Recording and alerting rules", "Recording rules precompute frequently used expressions into new time series; alerting rules evaluate conditions and send firing alerts to Alertmanager.", "Precomputation improves expensive dashboards and standardizes expressions; alerts convert symptoms into actionable notifications.", "Use recording rules for repeated aggregations and SLI calculations. Alert on user impact and sustained conditions with appropriate for durations.", ["Name recording rules consistently, often level:metric:operations.", "Preserve useful labels but drop needless cardinality.", "An alert should include severity, summary, impact, ownership, and runbook link."], "InfraPilot can consume stable recording rules for 5xx rate and p95 instead of embedding service-specific raw metric names in tool code.")
story += [p("Prometheus limitations and production patterns", "H2x")]
story += bullets(["Prometheus is usually eventually consistent and scrape-based; very short events can be missed unless represented by counters.", "Single-node local storage is not indefinite long-term analytics. Use retention planning and remote storage systems when required.", "HA Prometheus replicas improve availability but require downstream deduplication.", "Federation or remote write can support larger topologies, but cardinality and tenancy must still be managed.", "Use exemplars and trace IDs carefully; never place arbitrary IDs into metric labels."])
for q, a in [
    ("Why did kubectl top initially show metrics unavailable?", "Metrics Server had only just started and needed successful kubelet scrapes before pod metrics existed. In local kind clusters, kubelet certificates often require the insecure TLS flag for demonstration, but production should use valid trust rather than disabling verification."),
    ("Why use rate() on a counter?", "The raw counter is cumulative and resets on restart. rate() estimates per-second change across a range and accounts for resets, producing a comparable traffic or error signal."),
    ("Why must le remain in classic histogram aggregation?", "Each le value identifies a cumulative bucket boundary. histogram_quantile needs the bucket distribution, so sum by (le, other grouping labels) must preserve le."),
    ("How do you choose histogram buckets?", "Start from SLOs and expected distribution. Include boundaries around acceptable and unacceptable latency, then verify bucket occupancy. Too few buckets reduce precision; too many multiply series cardinality."),
    ("What is a cardinality explosion?", "A label receives many distinct values, multiplying series across all other labels. Memory, storage, scrape, and query costs rise sharply. Remove unbounded labels, aggregate earlier, and enforce instrumentation reviews."),
    ("What is wrong with hard-coded payment metric names for every service?", "It couples the generic evidence tool to one demo service and can return empty or misleading results. The tool needs a service-to-metric contract, standardized RED metrics, discovery metadata, or recording rules with consistent labels."),
]: story += qa(q, a)

# Cross tech scenarios
story += [PageBreak(), p("11. Cross-technology design scenarios", "Section")]
scenarios = [
    ("Design a production investigation execution model", "POST /investigations validates access, creates a PENDING run in PostgreSQL, and enqueues its ID in a durable queue. A worker obtains a lease, runs a checkpointed LangGraph, persists append-only node events and normalized evidence, and renews the lease. SSE reads the persisted event stream with Last-Event-ID support. Idempotency keys prevent duplicate runs; cancellation and retry policies are explicit. API and worker scale independently."),
    ("Protect the Kubernetes control plane", "Use per-cluster service accounts with minimal read verbs for evidence and a separate narrowly scoped remediation identity. Add namespace and workload allow-lists, authenticated RBAC, approval expiry, proposal hashes, target revalidation, secret redaction, network policies, and immutable audit events. Never mount a broad developer kubeconfig into a production backend."),
    ("Improve RAG quality", "Create a labeled set of incident queries and relevant runbook chunks. Add heading-aware chunks, service/environment/version metadata, hybrid lexical-vector retrieval, MMR or reranking, score thresholds, source citations, and abstention. Track Recall@k plus grounded diagnosis metrics. Re-index incrementally and alert on freshness failures."),
    ("Scale PostgreSQL and pgvector", "Measure first. Tune SQL and indexes, separate transactional and retrieval connection pools, batch ingestion, add read replicas for read-heavy APIs where consistency allows, partition by tenant or retention only when justified, and consider a dedicated vector system only after pgvector becomes the measured bottleneck. Maintain backups, PITR, vacuum, and extension upgrade procedures."),
    ("Make model-provider failures survivable", "Use deadlines, bounded retries with jitter for transient failures, circuit breakers, provider error classification, model capability validation, and fallbacks only when output contracts are compatible. Persist progress before calls, resume from checkpoints, expose partial evidence, and track error rate, latency, tokens, and fallback usage per model."),
    ("Evaluate the agent", "Build replayable incident fixtures with expected evidence, root cause, and safe action. Measure tool-selection precision/recall, time and calls to sufficient evidence, unsupported claims, cause ranking, check usefulness, confidence calibration, remediation acceptance, and unsafe-action rate. Run deterministic unit tests plus stochastic repeated evaluations across prompt/model versions."),
    ("Handle a stale remediation proposal", "Bind the proposal to incident/run ID, target UID or resource version, proposed action, and hash. At approval and execution, verify authorization, approval age, current target state, and unchanged proposal version. If state drifted, invalidate the approval and require a refreshed investigation or proposal."),
    ("Support multiple clusters and tenants", "Resolve an authenticated tenant and cluster scope before any query. Store cluster and tenant identifiers on every incident, run, evidence, document, and audit row; enforce database row policies or service-layer authorization; route to cluster-scoped MCP servers or credentials; partition secrets and queues; and include scope in vector filters."),
]
for title, body in scenarios:
    story += [p(title, "H2x"), p(body, "Callout")]

# Question bank
story += [PageBreak(), p("12. InfraPilot interview question bank", "Section")]
story += [p("These questions are intentionally project-specific. The strongest answer is honest about what exists today and precise about the next production improvement.")]
question_bank = [
    ("What user journey does InfraPilot support?", "An operator creates an incident, starts or reruns an investigation, watches progress, reviews evidence and grounded analysis, examines retrieved runbooks and history, reviews a remediation proposal, approves or rejects it, and executes only an allow-listed action. All important stages are persisted for later inspection."),
    ("Why FastAPI?", "It offers typed Pydantic contracts, generated OpenAPI, dependency injection, async I/O, and straightforward SSE support. Those fit a Python-based agent backend. The choice does not remove the need for service layers, durable work queues, or security."),
    ("Why Next.js?", "It supports a component-based operational dashboard, file routing, server/client rendering choices, and a good TypeScript ecosystem. InfraPilot uses it as the operator experience while FastAPI remains the control-plane API."),
    ("Why LangGraph?", "The investigation has branching, a cyclic tool loop, shared typed state, progressive updates, and potential pause/resume needs. LangGraph makes those control-flow concerns explicit and testable."),
    ("Why MCP?", "MCP separates reasoning from infrastructure adapters through discoverable typed contracts. Kubernetes and Prometheus integration can evolve independently and can be reused by another compatible host."),
    ("Why PostgreSQL and pgvector together?", "The application needs transactions and relational audit data as well as semantic runbook retrieval. One system reduces operational complexity and enables metadata filters and joins with vector search."),
    ("How is evidence grounded?", "The model receives live results from bounded read-only tools plus retrieved knowledge. The analysis schema separates confirmed facts from possible causes and recommended checks. Evidence and provenance are persisted. This improves grounding but does not prove every model claim, so evaluation and citation checks remain necessary."),
    ("What does confidence mean?", "It is a model-produced estimate constrained to a numeric range, not a statistically calibrated probability. It should be treated as an aid and calibrated against labeled incidents before it drives automation."),
    ("How are failures represented?", "The run reaches an explicit failed terminal state, stores a safe error, and retains partial state gathered before failure. The UI can offer rerun while preserving prior attempts for audit."),
    ("How does rerun work?", "Rerun creates a new investigation attempt for the same incident rather than overwriting the old one. That preserves history and lets users compare failures, evidence, model configuration, and outcomes."),
    ("Why not resume the same failed row?", "A new attempt has cleaner audit semantics and avoids mixing state from incompatible configurations. Resume can be added for checkpoint-safe transient failures, but its semantics must identify exactly which state and side effects are reused."),
    ("How do you stop an infinite agent loop?", "A hard tool-iteration cap and conditional routing terminate the loop. Production should also limit tokens, wall time, tool calls per type, and repeated identical calls, and add an evidence-sufficiency decision."),
    ("How do you prevent duplicated evidence?", "Normalize evidence by tool, target, time range, and content hash; deduplicate before prompt construction while preserving raw source records for audit. The current implementation can be extended with this deterministic layer."),
    ("What if one tool fails?", "Return a typed tool error as evidence, continue with independent checks when useful, and let analysis state the gap. Fail the entire investigation only when required evidence or the reasoning provider cannot proceed."),
    ("How do you avoid prompt injection from logs?", "Delimit logs as untrusted data, instruct the model not to follow instructions inside evidence, redact secrets, restrict tools and execution in code, and detect suspicious content. The allow-listed executor ensures injected text cannot become a shell command."),
    ("How do you validate model outputs?", "Use strict Pydantic or JSON schemas, enums, field bounds, and semantic checks such as target/action consistency. Retry bounded parsing failures and persist invalid-output diagnostics without exposing sensitive prompts."),
    ("Why use different models?", "Tool calling and structured reasoning have different capability and cost profiles. A tool-capable model handles selection; a stronger structured model handles analysis, with a compatible fallback. This separation also isolates provider failures and supports targeted evaluation."),
    ("Why was Groq failing?", "The failures were associated with model-call or structured-output compatibility and provider behavior rather than Kubernetes evidence collection. The correct fix is to inspect the exact provider error, validate the chosen model's tool/structured-output support, align schemas and parsing, and add a compatible fallback instead of silently bypassing the agent."),
    ("How would you make provider configuration safe?", "Validate model IDs and capabilities at startup, use typed settings, keep API keys in secret stores, expose non-secret active configuration, and run a startup or deployment smoke test for both tool calling and structured output."),
    ("How do you calculate error rate?", "Use PromQL rate over request counters, aggregate error statuses and divide by all requests over the same window. Guard against a zero denominator and preserve the service labels needed for grouping."),
    ("How do you calculate p95?", "For a classic histogram, apply rate to bucket counters, aggregate by le and desired dimensions, then call histogram_quantile(0.95, ...). Bucket design determines precision."),
    ("Why did /metrics initially return no payment metrics?", "The running image or route did not expose the instrumented metrics until the Dockerfile/application was corrected and the image redeployed. After traffic, the counter and histogram series appeared. This illustrates verifying the deployed artifact, not only local source."),
    ("How do Docker Compose and Kubernetes differ here?", "Compose runs the InfraPilot stack and demo dependencies locally. Kubernetes is the observed environment for cluster evidence and remediation tests. A mounted kubeconfig lets the containerized backend reach the host kind cluster, but production should use in-cluster identities instead."),
    ("Why could the dashboard show service inventory unavailable while containers were healthy?", "Container health only proves the Compose processes are alive. Inventory calls the Kubernetes API through a configured context; an invalid mounted context made that separate dependency unavailable. Health should be dependency-specific."),
    ("How should Kubernetes context configuration work?", "Resolve a stable cluster identifier to a credential at deployment time, validate it at readiness, and avoid hard-coded developer context assumptions. In production, run in cluster and use a service account or a controlled multi-cluster credential broker."),
    ("What is the remediation allow-list?", "A server-side mapping from a small action enum to trusted implementation code and validation. InfraPilot permits restart deployment. A proposal's displayed command is explanatory only and is never passed to a shell."),
    ("Why patch a deployment annotation to restart it?", "Changing the pod-template metadata causes Kubernetes to create a new ReplicaSet and roll pods according to deployment strategy. It uses the native controller rather than manually deleting pods, but rollout status still needs observation."),
    ("How do you know remediation succeeded?", "An API call succeeding means the change was accepted, not that service health recovered. A stronger executor waits for rollout, checks desired/available replicas, restarts/errors/latency, records before/after evidence, and reports partial or failed outcomes."),
    ("What race conditions exist in approval?", "Two approvers or executors could act concurrently, state might change after proposal, and a retry could duplicate execution. Prevent them with database-guarded transitions, proposal versions, idempotency keys, expiry, target revalidation, and an execution record."),
    ("What should be in an audit log?", "Actor, authenticated scope, incident/run/proposal IDs, decision, reason, action enum, target identity, proposal hash/version, timestamps, execution attempt, before/after state, result, errors, and correlation IDs. Protect integrity and retention."),
    ("How would you add RBAC?", "Define roles and resource scopes, authenticate users or service identities, enforce authorization at every route and execution boundary, carry tenant/cluster/namespace scope into queries and retrieval filters, and test denial paths. UI visibility is not authorization."),
    ("How do you redact secrets?", "Prefer not to retrieve them; restrict Kubernetes resources and log scopes. Then apply deterministic patterns and structured-field redaction before persistence, prompts, streams, and logs. Add organization-specific detectors and test for common token formats."),
    ("How would you support rollback?", "Not every action is reversible. Model an explicit compensating action only when pre-change state is captured and safe restoration is possible. For restarts, rollback is usually unnecessary; for image or config changes, use deployment revision or GitOps rollback with approval."),
    ("How would GitOps change remediation?", "The executor would propose or create an auditable repository change or pull request rather than directly mutating the cluster. Policy, review, CI, and the reconciler become the control path. Emergency actions may remain separate and tightly controlled."),
    ("How do you observe the agent itself?", "Emit traces for graph nodes, model calls, token use, provider/model, tool requests/results, retries, latency, RAG scores, state transitions, queue time, and outcome. Use correlation IDs across API, worker, MCP, and database records."),
    ("Which agent SLOs matter?", "Availability of accepting jobs, time to first evidence, time to completed investigation, successful-run ratio, grounded-answer rate, useful-evidence recall, and remediation decision/execution latency. Cost and provider rate limits are guardrails."),
    ("How would you load-test InfraPilot?", "Separate API ingestion, SSE fan-out, worker throughput, model-provider limits, MCP/Kubernetes calls, PostgreSQL pool contention, and vector queries. Use realistic incidents, cap external impact, and report queue latency and p95 end-to-end completion."),
    ("How do you cache safely?", "Cache embeddings by content/model version and possibly immutable runbook retrieval. Avoid caching live cluster evidence beyond a short freshness window. Include tenant, cluster, service, query, model, and permissions in cache keys."),
    ("How do you control cost?", "Bound iterations, tokens, retrieved context, concurrency, and retries; route simple structured tasks to smaller capable models; cache embeddings; use recording rules; and track cost per successful investigation. Do not trade away safety or evidence quality blindly."),
    ("How do you handle context-window limits?", "Normalize and summarize tool output, retrieve only relevant chunks, deduplicate, prioritize recent/high-signal evidence, reserve tokens for output, and store full raw evidence outside the prompt with references."),
    ("How would you add log search at scale?", "Do not pull unlimited pod logs into the model. Query a log backend with bounded time, labels, patterns, and limits; aggregate recurring errors; preserve links/provenance; and retrieve details only when the agent justifies it."),
    ("Why separate confirmed facts and possible causes?", "Evidence and inference have different epistemic status. The schema helps operators see what tools directly observed versus what the model inferred, reducing overconfidence and making follow-up checks actionable."),
    ("How should confidence be calibrated?", "Run labeled incidents repeatedly, bin predictions by confidence, compare observed correctness, and compute calibration error or Brier-like measures. Adjust prompts or mapping and use confidence only with evidence completeness and policy gates."),
    ("What is the role of historical incidents?", "They provide prior symptoms, root causes, and successful actions that can inform hypotheses. They must not be treated as current facts; match by relevance and outcome quality, include dates and scope, and avoid copying stale actions."),
    ("How would you improve historical retrieval?", "Embed incident summaries and evidence, apply service/severity/environment filters, combine semantic score, recency, and verified-resolution quality, deduplicate recurring incidents, and evaluate whether retrieved history improves diagnosis."),
    ("What data should never enter an LLM prompt?", "Secrets, credentials, tokens, private keys, unrestricted personal data, unnecessary customer payloads, and data disallowed by policy. Apply minimization, redaction, access checks, and provider data-handling controls before prompt construction."),
    ("How would you deploy the backend on Kubernetes?", "Use a Deployment for stateless API replicas, separate worker Deployment, Services, ConfigMaps and Secrets, migration Job, service accounts, network policies, readiness/liveness/startup probes, resource requests/limits, PodDisruptionBudget, autoscaling signals, and external PostgreSQL or a managed operator."),
    ("Why separate API and worker deployments?", "API latency and availability should not be coupled to long-running model workflows. Workers need different concurrency, timeouts, credentials, autoscaling signals, and restart semantics."),
    ("What does idempotency mean here?", "Repeating the same accepted request or job should not create unintended duplicate effects. Use client idempotency keys for creation, unique job/execution constraints, guarded state transitions, and idempotent Kubernetes patches or reconciliation."),
    ("What happens if the worker dies after changing Kubernetes but before persisting success?", "The result is uncertain. Persist an execution intent first, attach an idempotency marker to the target if possible, inspect actual cluster state on retry, and reconcile rather than blindly executing again."),
    ("How would you support cancellation?", "Persist a cancellation request, have workers check it between nodes and before side effects, propagate cancellation to model/tool calls, mark the run cancelled, and never interrupt an unsafe critical section without reconciliation."),
    ("How do you test model-dependent behavior deterministically?", "Inject fake model and tool interfaces that return known typed outputs for unit tests. Keep a separate stochastic evaluation suite against real models and record prompt/model versions and seeds where supported."),
    ("What is contract testing for MCP?", "Verify discovery, names, descriptions, JSON argument schemas, required fields, result and error shapes, timeouts, and capability negotiation across client and server versions. Use fixtures that do not require a live production cluster."),
    ("What is the biggest current observability gap?", "The system should expose complete traces and metrics across API, queued run, graph nodes, LLM calls, MCP calls, retrieval, database, approval, and executor with one correlation ID. UI status alone is insufficient."),
    ("What would you show in a demo?", "Create a deliberately failing demo service, generate traffic, open an incident, start investigation, show live evidence and runbook retrieval, explain facts versus hypotheses, approve a safe restart, verify rollout and metrics recovery, and show the persistent audit trail."),
    ("How do you explain a failed demo honestly?", "Show the retained partial evidence and error boundary, identify whether failure came from provider, tool, database, or cluster, rerun as a new attempt after correcting the dependency, and explain the production resilience improvement."),
    ("What did you personally learn?", "A strong answer is that agent quality is mainly systems engineering: typed contracts, evidence design, bounded loops, persistence, observability, evaluation, and privilege separation. The model is one component, not the whole product."),
]
for i, (q, a) in enumerate(question_bank, 1):
    story += qa(f"{i}. {q}", a)

# Rapid revision
story += [PageBreak(), p("13. Rapid revision sheets", "Section")]
story += [p("One-line distinctions", "H2x")]
distinctions = [
    ("LangChain", "Composable AI integrations: models, messages, tools, retrievers, schemas, and agents."),
    ("LangGraph", "Explicit stateful orchestration for branching, loops, persistence, interrupts, and durable execution."),
    ("RAG", "Retrieve external knowledge at runtime and use it to ground generation."),
    ("Vector database", "Operational system for storing embeddings and performing similarity search with filters and indexes."),
    ("pgvector", "PostgreSQL extension for vector types, operators, exact search, HNSW, and IVFFlat."),
    ("PostgreSQL", "Transactional system of record using relational constraints, MVCC, indexes, and durable storage."),
    ("FastAPI", "Typed Python ASGI API framework with Pydantic, dependency injection, OpenAPI, and async support."),
    ("MCP", "JSON-RPC protocol boundary exposing AI-facing tools, resources, and prompts."),
    ("Prometheus", "Pull-based labeled time-series monitoring system queried with PromQL."),
]
dt = Table([[p("Technology", "Small"), p("Interview definition", "Small")]] + [[p(a, "Bodyx"), p(b, "Bodyx")] for a,b in distinctions], colWidths=[38*mm,144*mm], repeatRows=1)
dt.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),NAVY),("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),0.4,LINE),("VALIGN",(0,0),(-1,-1),"TOP"),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,LIGHT]),("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
story += [dt]
story += [p("Answer framework", "H2x")]
story += [p("Use <b>C-C-T-E-N</b>: <b>Context</b> - the incident-response problem; <b>Choice</b> - the technology or design; <b>Trade-off</b> - what it costs or does not solve; <b>Evidence</b> - the implemented flow, test, metric, or behavior; <b>Next</b> - the production improvement. This structure sounds like engineering judgment rather than memorized definitions.", "Callout")]
story += [p("High-value comparisons", "H2x")]
for item in [
    "Agent vs chain: adaptive next step versus fixed sequence.",
    "SSE vs WebSocket: server-to-client event stream versus bidirectional connection.",
    "BackgroundTask vs queue: same-process best-effort work versus durable worker execution.",
    "Histogram vs summary: server-side aggregatable buckets versus client-side quantiles.",
    "Exact vs ANN: perfect nearest-neighbor ranking versus speed with recall trade-off.",
    "HNSW vs IVFFlat: graph-based high recall and memory cost versus clustered lists and probe tuning.",
    "RAG vs fine-tuning: current attributable knowledge versus learned behavior/patterns.",
    "MCP vs REST: AI capability protocol versus general HTTP resource API.",
    "Graph checkpoint vs product database: orchestration recovery state versus canonical queryable audit record.",
    "Proposal vs execution: probabilistic recommendation versus deterministic authorized side effect.",
]: story += bullets([item])

story += [p("Official references", "H2x")]
refs = [
    "LangChain overview: https://docs.langchain.com/oss/python/langchain/overview",
    "LangChain agents: https://docs.langchain.com/oss/python/langchain/agents",
    "LangChain retrieval and RAG: https://docs.langchain.com/oss/python/langchain/retrieval",
    "LangGraph thinking guide: https://docs.langchain.com/oss/python/langgraph/thinking-in-langgraph",
    "LangGraph interrupts: https://docs.langchain.com/oss/python/langgraph/interrupts",
    "LangChain MCP adapters: https://docs.langchain.com/oss/python/langchain/mcp",
    "MCP architecture: https://modelcontextprotocol.io/specification/2025-06-18/architecture",
    "MCP server primitives: https://modelcontextprotocol.io/specification/2025-06-18/server/index",
    "MCP transports: https://modelcontextprotocol.io/specification/2025-06-18/basic/transports",
    "FastAPI request bodies and OpenAPI: https://fastapi.tiangolo.com/tutorial/body/",
    "FastAPI dependencies: https://fastapi.tiangolo.com/tutorial/dependencies/",
    "FastAPI Server-Sent Events: https://fastapi.tiangolo.com/tutorial/server-sent-events/",
    "FastAPI background tasks: https://fastapi.tiangolo.com/tutorial/background-tasks/",
    "pgvector official documentation: https://github.com/pgvector/pgvector",
    "PostgreSQL concurrency control and MVCC: https://www.postgresql.org/docs/current/mvcc.html",
    "Prometheus concepts: https://prometheus.io/docs/concepts/",
    "Prometheus metric types: https://prometheus.io/docs/concepts/metric_types/",
    "PromQL functions: https://prometheus.io/docs/prometheus/latest/querying/functions/",
    "Prometheus recording rules: https://prometheus.io/docs/practices/rules/",
]
story += bullets(refs)
story += [Spacer(1, 8 * mm), p("Final reminder", "H2x"), p("You do not need to present InfraPilot as finished production software. Present it as a working, tested platform with deliberate safety boundaries, then show that you understand the reliability, security, evaluation, and scaling work required for production. That combination is stronger than overclaiming.", "Callout")]

doc.build(story)
print(OUT)
