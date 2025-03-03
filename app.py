import os
from groq import Groq
import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv() # Corrected line

# Set API keys from environment variable
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

if not GROQ_API_KEY or not GOOGLE_API_KEY:
    st.error("⚠️ API keys for Groq and Gemini are required. Please set them as Streamlit secrets.")
    st.stop()

# Initialize clients
try:
    groq_client = Groq(api_key=GROQ_API_KEY)
    genai.configure(api_key=GOOGLE_API_KEY)
except Exception as e:
    st.error(f"Error initializing API clients: {e}")
    st.stop()


# Apply custom styles for a premium feel
st.markdown(
    """
    <style>
    /* Main theme */
    .main {
        background: linear-gradient(135deg, #1f1c2c, #362e5b);
        color: #fff;
        font-family: 'Poppins', sans-serif;
    }

    /* FIXIFOX Title */
    .title-container {
        background: linear-gradient(90deg, #6c5ce7, #a29bfe);
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
    }

    /* Custom button styles */
    .button-container {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        margin: 20px 0;
    }

    .custom-button {
        background: linear-gradient(90deg, #6c5ce7, #8e44ad);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
        margin: 5px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }

    .custom-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 7px 15px rgba(0,0,0,0.3);
        background: linear-gradient(90deg, #8e44ad, #6c5ce7);
    }

    /* Code input area */
    .stTextArea textarea {
        background-color: #2d3436;
        color: #eee;
        border: 1px solid #6c5ce7;
        border-radius: 10px;
        font-family: 'Courier New', monospace;
        padding: 15px;
        box-shadow: inset 0 2px 10px rgba(0,0,0,0.2);
    }

    /* Results area */
    .result-container {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        border-left: 5px solid #6c5ce7;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }

    /* Tooltips */
    .tooltip {
        position: relative;
        display: inline-block;
    }

    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: #555;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
    }

    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }

    /* Other elements */
    .stAlert {
        border-radius: 10px;
        border: none;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }

    h1, h2, h3 {
        font-weight: 700;
        color: #fff;
    }

    .footer {
        text-align: center;
        margin-top: 50px;
        padding: 20px;
        font-size: 12px;
        color: #ccc;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: rgba(108, 92, 231, 0.2);
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        border: none;
    }

    .stTabs [aria-selected="true"] {
        background-color: rgba(108, 92, 231, 0.8);
    }

    /* Custom code block styles */
    .syntax-highlight {
        background-color: #1e1e2e;
        border-radius: 10px;
        padding: 15px;
        font-family: 'Courier New', monospace;
        overflow-x: auto;
        border-left: 3px solid #6c5ce7;
        color: #f8f8f2;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Function to explain code with Gemini
def explain_code_with_gemini(code, is_error=False):
    model = genai.GenerativeModel('gemini-2.0-flash')

    if is_error:
        prompt = f"""Explain the following error in the code step-by-step in a very beginner-friendly way:
        1. What caused the error
        2. How to fix it
        3. Provide a simple explanation of the concept that's related to this error

        Code/Error:
        {code}"""
    else:
        prompt = f"""Explain the following code step-by-step in a very beginner-friendly way:
        1. What each part of the code does
        2. How the different parts work together
        3. Any potential improvements or best practices to consider

        Code:
        {code}"""

    response = model.generate_content(prompt)
    return response.text.strip()

# Function to query Groq for fixed, secure code
def get_fixed_code_with_groq(code, model="qwen-2.5-coder-32b", max_tokens=2000):
    messages = [
        {"role": "system", "content": "You are a security and code quality expert. Detect vulnerabilities and bugs in the code. Return ONLY the fixed, secure code with brief comments explaining the changes."},
        {"role": "user", "content": f"Fix this code and add helpful comments to explain your changes:\n\n{code}"}
    ]

    completion = groq_client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.2,
        max_tokens=max_tokens,
        top_p=0.9,
        stream=True
    )

    fixed_code = ""
    for chunk in completion:
        fixed_code += chunk.choices[0].delta.content or ""
    return fixed_code.strip()

# Function to generate code flow diagram
def generate_code_flow(code):
    model = "qwen-2.5-coder-32b"
    prompt = f"""Generate a clear, beginner-friendly code flow diagram for the following code.

    Use Mermaid.js flowchart syntax with the following guidelines:
    1. Use a top-down (TD) layout for better readability
    2. Use simple boxes for functions and processes
    3. Use diamond shapes for decision points
    4. Use rounded boxes for start/end points
    5. Use clear, concise labels (maximum 5-7 words per node)
    6. Group related operations where possible
    7. Limit diagram complexity (max 10-15 nodes)
    8. Include clear arrows with short descriptions
    9. Add colors to distinguish different types of operations (e.g., blue for input, green for processing, yellow for decisions)

    The diagram should explain the code to absolute beginners. Focus on the main flow and purpose rather than every single line.

    Code:
    {code}"""

    response = groq_client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2000
    )

    # Extract mermaid code from response
    content = response.choices[0].message.content

    # Process the response to ensure it's clean mermaid code
    if "```mermaid" in content:
        # Extract just the mermaid code
        start = content.find("```mermaid")
        end = content.find("```", start + 10)
        if end != -1:
            mermaid_code = content[start+10:end].strip()

            # Ensure the diagram uses TD (top-down) direction for clarity
            if "graph " in mermaid_code and "TD" not in mermaid_code:
                mermaid_code = mermaid_code.replace("graph ", "graph TD ")

            return mermaid_code

    # If no mermaid code found or there's an issue, generate a simple diagram
    return """graph TD
    A[Start Program] --> B[Initialize Variables]
    B --> C[Process Input]
    C --> D{Check Conditions}
    D -->|Condition Met| E[Execute Main Logic]
    D -->|Condition Not Met| F[Handle Exception]
    E --> G[Generate Output]
    F --> G
    G --> H[End Program]

    style A fill:#d0f0c0,stroke:#333,stroke-width:2px
    style D fill:#fffacd,stroke:#333,stroke-width:2px
    style H fill:#d0f0c0,stroke:#333,stroke-width:2px
    style E fill:#b0e0e6,stroke:#333,stroke-width:2px
    style F fill:#ffb6c1,stroke:#333,stroke-width:2px"""

# Function for interactive debugging mode
def interactive_debug(code, error_message):
    model = "qwen-2.5-coder-32b"
    prompt = f"""You are an expert debugging assistant.

    CODE:
    ```
    {code}
    ```

    ERROR:
    ```
    {error_message}
    ```

    Provide a detailed debugging analysis:
    1. Identify the exact line and cause of the error
    2. Explain why this error occurs in simple terms
    3. Provide a specific fix for the error
    4. Show the corrected code
    5. Explain how to prevent similar errors in the future

    Format your response in clear markdown with code examples.
    """

    response = groq_client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2000
    )

    return response.choices[0].message.content.strip()

def run_security_scan(code_input):
    """
    Runs a security and vulnerability scan using AI.

    Args:
        code_input (str): The code to be scanned.

    Returns:
        str: A security report.
    """
    model = "qwen-2.5-coder-32b"  # Or your chosen Groq model
    prompt = f"""
    Analyze the following code for security vulnerabilities and potential issues. 
    Provide a detailed report including:
    1. Identified vulnerabilities (e.g., injection, insecure functions, etc.)
    2. Severity of each vulnerability (High, Medium, Low)
    3. Specific code lines where vulnerabilities are found.
    4. Recommendations for fixing each vulnerability.
    5. Overall code quality assessment and suggestions for improvement.
    
    Code:
    ```
    {code_input}
    ```
    """

    try:
        response = groq_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error during AI security scan: {e}"

# Main Streamlit UI
def main():
    # ... (Your existing Streamlit UI code) ...

    with tabs[0]:
        # ... (Your existing code input and button logic) ...

        if security_clicked:
            if code_input.strip():
                st.markdown('<div class="result-container">', unsafe_allow_html=True)
                st.markdown("### 🔐 Security & Vulnerability Report (AI Powered)")

                with st.spinner("Scanning for vulnerabilities (AI)..."):
                    security_report = run_security_scan(code_input)

                st.markdown(security_report)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.error("⚠️ Please enter some code to scan for vulnerabilities!")
# Main Streamlit UI
def main():
    # Custom title with HTML
    st.markdown(
        """
        <div class="title-container">
            <h1>🦊 FIXIFOX</h1>
            <p>Premium AI-Powered Code Assistant, Debugger & Security Scanner</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Sidebar without animations
    with st.sidebar:
        st.markdown("## 🦊 FIXIFOX Features")

        st.markdown("### Premium Features")
        st.markdown("""
        - 🔍 AI Code Explanation
        - 🔧 Auto-Fix & Secure Code
        - 📊 Flow Diagrams
        - 🔐 Security Vulnerability Scans
        - 🐞 Interactive Debugging Mode
        """)

        st.markdown("### Powered By")
        st.markdown("""
        - 🤖 Gemini 2.0 Flash
        - 🧠 Groq API with Qwen 2.5 Coder
        """)

        st.markdown("---")

    # Main content area with tabs
    tabs = st.tabs(["💻 Code Assistant", "🐞 Debug Mode", "⚙️ Settings"])
    diagram_clicked = False
    security_clicked = False

    with tabs[0]:
        st.markdown("### 🔮 Paste your code below")

        # Code input with syntax highlighting
        code_input = st.text_area("", height=300, placeholder="Paste your code here...", key="code_input")

        # Action buttons with enhanced UI
        st.markdown('<div class="button-container">', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                '<button class="custom-button" id="explain-btn" onclick="document.querySelector(\'#explain-btn-hidden\').click()">🔍 Explain Code (Gemini)</button>',
                unsafe_allow_html=True
            )
            explain_clicked = st.button("🔍 Explain Code", key="explain-btn-hidden", help="Get a beginner-friendly explanation of your code")

            st.markdown(
                '<button class="custom-button" id="diagram-btn" onclick="document.querySelector(\'#diagram-btn-hidden\').click()">📊 Generate Flow Diagram</button>',
                unsafe_allow_html=True
            )
            diagram_clicked = st.button("📊 Generate Flow Diagram", key="diagram-btn-hidden", help="Create a visual diagram of your code flow")

        with col2:
            st.markdown(
                '<button class="custom-button" id="fix-btn" onclick="document.querySelector(\'#fix-btn-hidden\').click()">🔧 Fix & Secure Code</button>',
                unsafe_allow_html=True
            )
            fix_clicked = st.button("🔧 Fix & Secure Code", key="fix-btn-hidden", help="Get an improved version of your code with fixes")

            st.markdown(
                '<button class="custom-button" id="security-btn" onclick="document.querySelector(\'#security-btn-hidden\').click()">🔐 Security Scan</button>',
                unsafe_allow_html=True
            )
            security_clicked = st.button("🔐 Security Scan", key="security-btn-hidden", help="Check your code for vulnerabilities and quality issues")

        st.markdown('</div>', unsafe_allow_html=True)

        # Process actions
        if explain_clicked:
            if code_input.strip():
                st.markdown('<div class="result-container">', unsafe_allow_html=True)
                st.markdown("### 🔍 Code Explanation")

                with st.spinner("Generating explanation..."):
                    explanation = explain_code_with_gemini(code_input)

                st.markdown(explanation)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.error("⚠️ Please enter some code to explain!")

        if fix_clicked:
            if code_input.strip():
                st.markdown('<div class="result-container">', unsafe_allow_html=True)
                st.markdown("### 🔧 Fixed & Secure Code")

                with st.spinner("Fixing and securing code..."):
                    fixed_code = get_fixed_code_with_groq(code_input)

                if fixed_code:
                    st.code(fixed_code, language='python')

                    # Copy button
                    if st.button("📋 Copy Fixed Code"):
                        st.code(fixed_code)
                        st.success("✅ Code copied to clipboard!")
                else:
                    st.warning("⚠️ No fixes found or generated. Double-check your code!")

                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.error("⚠️ Please enter some code to fix!")

        if diagram_clicked:
            if code_input.strip():
                st.markdown('<div class="result-container">', unsafe_allow_html=True)
                st.markdown("### 📊 Code Flow Diagram")

                with st.spinner("Generating flow diagram..."):
                    flow_diagram = generate_code_flow(code_input)

                st.markdown(f"```mermaid\n{flow_diagram}\n```")
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.error("⚠️ Please enter some code to generate a diagram!")

        if security_clicked:
            if code_input.strip():
                st.markdown('<div class="result-container">', unsafe_allow_html=True)
                st.markdown("### 🔐 Security & Vulnerability Report")

                with st.spinner("Scanning for vulnerabilities..."):
                    security_report = run_security_scan(code_input)

                st.markdown(security_report)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.error("⚠️ Please enter some code to scan for vulnerabilities!")

    with tabs[1]:
        st.markdown("### 🐞 Interactive Debugging Mode")
        st.markdown("Paste your code and the error message to get detailed debugging analysis")

        debug_code = st.text_area("Your code with errors:", height=250, key="debug_code")
        error_message = st.text_area("Error message or description of the issue:", height=100, key="error_message")

        if st.button("🐞 Debug Now", key="debug_button"):
            if debug_code.strip() and error_message.strip():
                st.markdown('<div class="result-container">', unsafe_allow_html=True)
                st.markdown("### 🔍 Debugging Analysis")

                with st.spinner("Analyzing your code..."):
                    debug_results = interactive_debug(debug_code, error_message)

                st.markdown(debug_results)

                # Also offer explanation
                if st.button("🧠 Explain Error For Beginners"):
                    with st.spinner("Generating beginner explanation..."):
                        beginner_explanation = explain_code_with_gemini(error_message, is_error=True)

                    st.markdown("### 🔰 Beginner-Friendly Explanation")
                    st.markdown(beginner_explanation)

                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.error("⚠️ Please provide both code and an error message to debug!")

    with tabs[2]:
        st.markdown("### ⚙️ FIXIFOX Settings")

        st.markdown("#### 🎨 UI Theme")
        theme = st.selectbox("Select theme:",
                             ["Dark Premium (Default)", "Neon Fox", "Midnight Coder", "Forest Green"],
                             index=0)

        st.markdown("#### 🤖 AI Models")
        explanation_model = st.selectbox("Explanation model:",
                                         ["Gemini 2.0 Flash (Default)", "Gemini 2.0 Pro"],
                                         index=0)

        code_fix_model = st.selectbox("Code fixing model:",
                                      ["Qwen 2.5 Coder 32B (Default)", "Qwen 2.5 Coder 7B", "Llama 3 70B"],
                                      index=0)

        st.markdown("#### ⚡ Performance")
        st.slider("Response detail level:", min_value=1, max_value=10, value=7)

        if st.button("💾 Save Settings"):
            st.success("✅ Settings saved successfully!")

    # Footer
    st.markdown(
        """
        <div class="footer">
            <p>FIXIFOX © 2025 | Premium AI-Powered Code Assistant</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()