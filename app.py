import os
import sys

# Set environment variables to disable CrewAI knowledge features FIRST
os.environ["CREWAI_KNOWLEDGE_DISABLED"] = "True"
os.environ["CREWAI_KNOWLEDGE_STORAGE_DISABLED"] = "True"

# Try to replace standard sqlite3 with pysqlite3
try:
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    # If pysqlite3 is not available, fall back to disabling knowledge features
    os.environ["CREWAI_KNOWLEDGE_DISABLED"] = "True"
    os.environ["CREWAI_KNOWLEDGE_STORAGE_DISABLED"] = "True"
    print("pysqlite3 not available, using standard sqlite3 with knowledge disabled")

import streamlit as st
import time
import json
from pathlib import Path
from crewai import Crew, Task, Process
from TutorTasks import (
    teaching_task,
    code_review_task,
    curriculum_task,
    quiz_task,
    coordination_task,
    task_to_strings,
)
# Your agent objects (must exist in TutorAgents.py)
from TutorAgents import (
    teaching_expert,
    code_reviewer,
    curriculum_planner,
    quiz_master,
    project_coordinator,
)
from streamlit_local_storage import LocalStorage
import re

# Set BASE_DIR to the current directory
BASE_DIR = Path(__file__).resolve().parent

# -------------------------
# Page config & CSS
# -------------------------
st.set_page_config(page_title="Pythonaut - AI Python Tutor", page_icon="🐍", layout="wide")

st.markdown(
    """
<style>
/* Fixed header section */
.header-container {
    position: sticky;
    top: 0;
    z-index: 100;
    padding: 5px 0;
    border-bottom: 1px solid #E5E7EB;
    margin-bottom: 10px;
}
.header { 
    font-size: 1.8rem; 
    font-weight: 700; 
    margin-bottom: 3px; 
    color: #FFD43B;
    text-align: center;
}
.sub { 
    color: #6B7280; 
    margin-bottom: 8px; 
    text-align: center;
    font-size: 0.9rem;
}
.instructions {
    background-color: rgba(255, 212, 59, 0.1);
    padding: 10px 12px;
    border-radius: 6px;
    border-left: 2px solid #FFD43B;
    margin: 8px auto;
    max-width: 800px;
    font-size: 0.85rem;
}

/* Chat container */
.chat-container {
    max-height: 65vh;
    overflow-y: auto;
    padding: 12px;
    background: #F7F7F8;
    border: 1px solid #E5E7EB;
    border-radius: 10px;
    margin-bottom: 15px;
}
.chat-row { 
    display: flex; 
    margin: 10px 0; 
}
.chat-row.user {
    justify-content: flex-end;
}
.bubble { 
    max-width: 80%; 
    padding: 10px 14px; 
    border-radius: 16px; 
    line-height: 1.4; 
    white-space: pre-wrap;
    word-wrap: break-word;
    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}
.bubble.user { 
    background: #E1F5FE; 
    color: #0E1117; 
    border-bottom-right-radius: 4px;
}
.bubble.ai { 
    background: #FFD43B; 
    color: #000; 
    border-left: 3px solid #37699F;
    border-bottom-left-radius: 4px;
}
.typing-indicator {
    display: flex;
    align-items: center;
    color: #666;
    font-style: italic;
    margin: 8px 0;
    font-size: 0.9rem;
}
.typing-dot {
    width: 6px;
    height: 6px;
    background-color: #666;
    border-radius: 50%;
    margin: 0 2px;
    animation: pulse 1.5s infinite ease-in-out;
}
.typing-dot:nth-child(2) {
    animation-delay: 0.2s;
}
.typing-dot:nth-child(3) {
    animation-delay: 0.4s;
}
@keyframes pulse {
    0%, 100% { opacity: 0.4; transform: scale(0.8); }
    50% { opacity: 1; transform: scale(1.2); }
}

.footer { 
    text-align: center; 
    color: #6B7280; 
    font-size: 0.8rem; 
    margin-top: 15px;
}

/* Disabled chat input */
.disabled-chat input {
    opacity: 0.5;
    cursor: not-allowed;
}

/* Reset button styling */
.reset-button {
    background-color: #f44336;
    color: white;
    border: none;
    padding: 6px 12px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.8rem;
    margin-top: 10px;
}
.reset-button:hover {
    background-color: #d32f2f;
}

/* Fix for chat input box */
.stChatInput > div > div {
    max-height: 100px !important;
    overflow-y: auto !important;
}

.stChatInput textarea {
    max-height: 80px !important;
    overflow-y: auto !important;
    resize: vertical !important;
}

/* Force reset when input is disabled */
.disabled-chat .stChatInput textarea {
    height: 38px !important;
    max-height: 38px !important;
}

/* Code block styling */
.code-block {
    background-color: #2d2d2d;
    color: #f8f8f2;
    padding: 12px;
    border-radius: 6px;
    overflow-x: auto;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 0.9em;
    margin: 8px 0;
    white-space: pre-wrap;
}
</style>
""",
    unsafe_allow_html=True,
)

# Add JavaScript to reset chat input
st.components.v1.html("""
<script>
// Function to reset chat input size
function resetChatInput() {
    const textareas = document.querySelectorAll('.stChatInput textarea');
    textareas.forEach(textarea => {
        textarea.style.height = '38px';
    });
}

// Listen for changes in the chat container to detect when new messages are added
const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
        if (mutation.addedNodes.length) {
            // Small delay to ensure the message is fully processed
            setTimeout(resetChatInput, 100);
        }
    });
});

// Start observing when the page loads
window.addEventListener('load', function() {
    const chatContainer = document.querySelector('.chat-container');
    if (chatContainer) {
        observer.observe(chatContainer, { childList: true, subtree: true });
    }

    // Also reset the input when the reset button is clicked
    const resetButton = document.querySelector('[data-testid="baseButton-secondary"]');
    if (resetButton) {
        resetButton.addEventListener('click', resetChatInput);
    }
});
</script>
""", height=0)

# -------------------------
# Session state
# -------------------------
if "local_storage" not in st.session_state:
    st.session_state.local_storage = LocalStorage()

if "messages" not in st.session_state:
    # Try to load existing chat
    st.session_state.messages = []
    chat_loaded = False

    # Try to load from local storage first
    try:
        saved_chat = st.session_state.local_storage.getItem("pythonaut_chat_history")
        if saved_chat and saved_chat.value:
            st.session_state.messages = json.loads(saved_chat.value)
            chat_loaded = True
    except:
        pass

    # Fallback to file loading
    if not chat_loaded:
        try:
            if os.path.exists("chat_history.json"):
                with open("chat_history.json", "r", encoding="utf-8") as f:
                    st.session_state.messages = json.load(f)
        except:
            st.session_state.messages = []

if "chat_started" not in st.session_state:
    st.session_state.chat_started = False

if "user_info" not in st.session_state:
    st.session_state.user_info = {"level": "beginner", "goals": "", "interests": ""}

if "processing" not in st.session_state:
    st.session_state.processing = False

# Add a key for chat input reset
if "chat_input_key" not in st.session_state:
    st.session_state.chat_input_key = 0

CHAT_SAVE_FILENAME = "chat_history.json"


# -------------------------
# Helpers
# -------------------------
def save_chat(filename=CHAT_SAVE_FILENAME):
    """Save chat history as a JSON file and to local storage."""
    try:
        # Save to file
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(st.session_state.messages, f, indent=2, ensure_ascii=False)

        # Also save to browser local storage
        st.session_state.local_storage.setItem("pythonaut_chat_history",
                                               json.dumps(st.session_state.messages))
    except Exception as e:
        # don't crash UI if saving fails; log in console
        print("Failed saving chat:", e)


def safe_extract_text(result_obj):
    """Best-effort textual extraction from Crew kickoff result."""
    if result_obj is None:
        return "No response (result was None)."
    # Common Crew result attributes
    for attr in ("raw", "output", "final_output", "result", "text"):
        if hasattr(result_obj, attr):
            val = getattr(result_obj, attr)
            if isinstance(val, str) and val.strip():
                return val
            # sometimes raw is an object/dict; convert to string
            try:
                return json.dumps(val, indent=2, ensure_ascii=False)
            except Exception:
                return str(val)
    # If it's a string directly
    if isinstance(result_obj, str):
        return result_obj
    # fallback
    try:
        return str(result_obj)
    except Exception:
        return "(No textual output available)"


def format_code_blocks(text):
    """Format code blocks in text with proper HTML and preserve quotes."""
    # Find all code blocks
    code_blocks = re.findall(r'```(?:python)?\s*(.*?)\s*```', text, re.DOTALL)

    # Replace each code block with formatted HTML
    for code in code_blocks:
        # Replace HTML entities with actual characters in code blocks
        unescaped_code = code.replace('&quot;', '"').replace('&#x27;', "'")
        # Wrap in code block div
        html_code = f'<div class="code-block">{unescaped_code}</div>'
        text = text.replace(f'```{code}```', html_code)

    return text


def typewriter_stream(text, placeholder, delay=0.015):
    """Stream characters into placeholder.markdown() with bubble styling."""
    # Show typing indicator first
    placeholder.markdown("""
    <div class="typing-indicator">
        Pythonaut is thinking 
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
    </div>
    """, unsafe_allow_html=True)

    # Add a small delay to simulate thinking
    time.sleep(1.5)

    # Now stream the text
    out = ""
    for ch in text:
        out += ch
        # Format code blocks
        formatted_out = format_code_blocks(out)
        placeholder.markdown(f'<div class="chat-row"><div class="bubble ai">{formatted_out}</div></div>',
                             unsafe_allow_html=True)
        time.sleep(delay)
    return out


# -------------------------
# Header with reset button
# -------------------------
col1, col2 = st.columns([6, 1])
with col1:
    st.markdown("""
    <div class="header-container">
        <div class="header">🐍 Pythonaut</div>
        <div class="sub">Your AI Python Tutor — from beginner to professional</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    if st.button("Reset Chat", type="secondary"):
        st.session_state.messages = []
        st.session_state.local_storage.deleteItem("pythonaut_chat_history")
        if os.path.exists(CHAT_SAVE_FILENAME):
            os.remove(CHAT_SAVE_FILENAME)
        st.session_state.chat_started = False
        st.session_state.chat_input_key += 1
        st.rerun()

# Instructions using native Streamlit markdown
st.markdown("### How to use Pythonaut:")
st.markdown("""
- **Introduce yourself** - Tell me about your Python experience level
- **Ask for explanations** - "Explain variables in Python" or "What are functions?"
- **Get code reviews** - Paste your code and ask for feedback
- **Request learning paths** - "Create a learning plan for data science"
- **Take quizzes** - "Test me on loops" or "Give me a quiz about classes"
""")

# Put initial assistant greeting if no messages exist
if not st.session_state.messages:
    greeting = (
        "Hello! I'm Pythonaut, your AI Python tutor. "
        "Tell me about your current experience with Python (beginner/intermediate/advanced), "
        "and what you'd like to achieve (web development, data analysis, automation, etc.)."
    )
    st.session_state.messages.append({"role": "assistant", "content": greeting})
    st.session_state.chat_started = True
    save_chat()

# -------------------------
# Render chat history
# -------------------------
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="chat-row user"><div class="bubble user">{msg["content"]}</div></div>',
                    unsafe_allow_html=True)
    else:
        formatted_content = format_code_blocks(msg["content"])
        st.markdown(f'<div class="chat-row"><div class="bubble ai">{formatted_content}</div></div>',
                    unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)


# -------------------------
# Process user input & assign tasks to agents correctly
# -------------------------
def process_user_input_and_run(user_input: str) -> str:
    """
    Decide which task to create and which agent should run it,
    assign the Task.agent properly and run Crew.kickoff() for that one task.
    Returns the textual result.
    """
    # normalize and infer
    lower = user_input.lower()
    skill = st.session_state.user_info.get("level", "beginner")
    goals = st.session_state.user_info.get("goals", "")

    # TEACHING INTENT DETECTION - Check this FIRST
    teaching_phrases = [
        "teach me", "explain", "what is", "how to", "learn python", 
        "step by step", "from start", "beginner guide", "tutorial",
        "concept", "lesson", "course", "understand", "help me learn"
    ]
    
    teaching_requested = any(phrase in lower for phrase in teaching_phrases)
    
    # If it's clearly a teaching request, route to teaching expert
    if teaching_requested:
        # Use the user's phrase as topic when appropriate, else generic "Getting started"
        topic = user_input if len(user_input.split()) < 30 else "Python programming from beginner to advanced"
        base_task = teaching_task(topic, skill, student_background="")
        desc, expected = task_to_strings(base_task)
        assigned_task = Task(
            description=desc,
            expected_output=expected or base_task.expected_output,
            agent=teaching_expert,
            output_file=getattr(base_task, "output_file", "teaching_report.md"),
            config={},
        )

        crew = Crew(agents=[teaching_expert], tasks=[assigned_task], process=Process.sequential, verbose=False)
        result = crew.kickoff()
        text = safe_extract_text(result)
        return text

    # Comprehensive code review detection
    code_review_phrases = [
        "review my code", "check this code", "debug", "code review",
        "what's wrong", "whats wrong", "error", "fix this",
        "why isn't this working", "can you tell me whats wrong",
        "what is wrong with this", "help with this code",
        "why is this not working", "this code doesn't work",
        "fix my code", "bug in my code", "help me fix"
    ]

    code_review_requested = any(phrase in lower for phrase in code_review_phrases)

    # Enhanced Python code detection
    has_python_code = False
    python_indicators = [
        "import ", "def ", "class ", "if ", "for ", "while ", "try:", "except:",
        "print(", "input(", "float(", "int(", "str(", "range(", "len(",
        " = ", " == ", " != ", " += ", " -= ", " *= ", " /= ",
        " and ", " or ", " not ", " in ", " is ", " with ", " as ",
        "from ", "return ", "yield ", "assert ", "raise ", "pass ", "break ", "continue "
    ]

    for indicator in python_indicators:
        if indicator in user_input:
            has_python_code = True
            break

    # Also check for common Python patterns
    if not has_python_code:
        if (re.search(r'[a-zA-Z_][a-zA-Z0-9_]*\s*=', user_input) or  # variable assignment
                re.search(r'[a-zA-Z_][a-zA-Z0-9_]*\s*\(', user_input) or  # function call
                re.search(r'("""|\'\'\'|"|\').*?("""|\'\'\'|"|\')', user_input) or  # strings
                re.search(r'#.*', user_input) or  # comments
                re.search(r'(if|for|while|def|class|try|except|with)\s+[a-zA-Z_]', user_input)):  # control flow
            has_python_code = True

    # Check for code blocks with backticks
    has_code_block = re.search(r"```(?:python)?\s*(.*?)\s*```", user_input, re.DOTALL | re.IGNORECASE)

    # If user is asking for code review or has Python code with a question, route to code reviewer
    if code_review_requested or (has_python_code and any(q in lower for q in ["?", "what", "why", "how", "help"])):
        # Extract code - use the entire input if no code block is found
        code = has_code_block.group(1) if has_code_block else user_input

        base_task = code_review_task(code, skill)
        desc, expected = task_to_strings(base_task)
        assigned_task = Task(
            description=desc,
            expected_output=expected or base_task.expected_output,
            agent=code_reviewer,
            output_file=getattr(base_task, "output_file", "code_review.md"),
            config={},
        )
        crew = Crew(agents=[code_reviewer], tasks=[assigned_task], process=Process.sequential, verbose=False)
        result = crew.kickoff()
        return safe_extract_text(result)

    # Curriculum path
    if any(p in lower for p in ("curriculum", "learning path", "syllabus", "study plan")):
        base_task = curriculum_task(goals, skill, time_availability="regular",
                                    specific_interests=st.session_state.user_info.get("interests", ""))
        desc, expected = task_to_strings(base_task)
        assigned_task = Task(
            description=desc,
            expected_output=expected or base_task.expected_output,
            agent=curriculum_planner,
            output_file=getattr(base_task, "output_file", "learning_plan.md"),
            config={},
        )
        crew = Crew(agents=[curriculum_planner], tasks=[assigned_task], process=Process.sequential, verbose=False)
        result = crew.kickoff()
        return safe_extract_text(result)

    # Quiz path
    if any(p in lower for p in ("quiz", "test me", "question", "exam")):
        topic = "Python basics"
        for cue in ("about", "on"):
            if cue in lower:
                idx = lower.find(cue) + len(cue)
                topic = user_input[idx:].strip(" :?") or topic
                break
        base_task = quiz_task(topic, skill)
        desc, expected = task_to_strings(base_task)
        assigned_task = Task(
            description=desc,
            expected_output=expected or base_task.expected_output,
            agent=quiz_master,
            output_file=getattr(base_task, "output_file", "quiz.md"),
            config={},
        )
        crew = Crew(agents=[quiz_master], tasks=[assigned_task], process=Process.sequential, verbose=False)
        result = crew.kickoff()
        return safe_extract_text(result)

    # Default fallback: use the coordinator
    base_task = coordination_task([f"user: {user_input}"], user_input, skill, goals)
    desc, expected = task_to_strings(base_task)
    assigned_task = Task(
        description=desc,
        expected_output=expected or base_task.expected_output,
        agent=project_coordinator,
        output_file=getattr(base_task, "output_file", "coordination_plan.md"),
        config={},
    )
    crew = Crew(agents=[project_coordinator], tasks=[assigned_task], process=Process.sequential, verbose=False)
    result = crew.kickoff()
    return safe_extract_text(result)

# -------------------------
# Chat input handling
# -------------------------
# Disable chat input if processing
if st.session_state.processing:
    st.markdown('<div class="disabled-chat">', unsafe_allow_html=True)

# Use a key that will change to force reset
user_input = st.chat_input(
    "Tell me about your Python experience or ask for a lesson...",
    disabled=st.session_state.processing,
    key=f"chat_input_{st.session_state.chat_input_key}"
)

if st.session_state.processing:
    st.markdown('</div>', unsafe_allow_html=True)

if user_input and not st.session_state.processing:
    # Set processing flag
    st.session_state.processing = True

    # append user message immediately
    st.session_state.messages.append({"role": "user", "content": user_input})
    save_chat()

    # Rerun to show the user message immediately
    st.rerun()

# Check if we need to process a user message
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user" and st.session_state.processing:
    # Get the last user message
    last_user_message = st.session_state.messages[-1]["content"]

    # Reserve a placeholder area for streaming assistant output
    placeholder = st.empty()

    # Run processing (assign tasks to agents and kickoff)
    try:
        ai_full_text = process_user_input_and_run(last_user_message)
    except Exception as e:
        # If Crew or Task creation throws, show the error but do not crash
        ai_full_text = f"Error while running agent task: {e}"

    # Stream into the placeholder character-by-character, then finalize
    streamed = typewriter_stream(ai_full_text, placeholder, delay=0.015)

    # Add assistant final message to history and save
    st.session_state.messages.append({"role": "assistant", "content": streamed})
    save_chat()

    # Increment the chat input key to force a reset
    st.session_state.chat_input_key += 1
    st.session_state.processing = False

    # Rerun to show the final state
    st.rerun()

# -------------------------
# Footer
# -------------------------
st.markdown("""
<div class="footer">
    <p>Pythonaut - AI Python Tutor | Built with CrewAI & Streamlit | 🇵🇸 Free Palestine</p>
</div>
""", unsafe_allow_html=True)