# **SYSTEM INSTRUCTION: Claude-to-Gemini Automation Pipeline**

**To Claude Code:**

The user wants to establish a highly automated pipeline to generate LinkedIn carousels. Your objective is to analyze the local project environment, select the best implementation path outlined below, and build a zero-manual-intervention bridge between yourself (Claude Code) and the Gemini API (using Google's latest model capabilities, including text and image generation).

## **1\. Objective & Requirements**

* **Goal:** Generate a complete LinkedIn carousel (Slide text outline \+ matching AI-generated slide background images) from a single topic prompt.  
* **Zero-Copy Workflow:** No copy-pasting text or downloading images manually from web browsers. Everything must be executed locally and saved into a shared workspace directory.  
* **Human-in-the-Loop:** The user only wants to provide the *topic idea/hook* and perform final approval.  
* **Output Assets:** A dedicated folder per carousel containing slide copy (slides.md) and a series of generated images (slide\_1.png ... slide\_N.png).

## **2\. Technical Paths to Analyze**

Analyze the workspace and choose one of the two paths below to implement. **Path A (The Orchestrated Script) is highly recommended for stability and execution speed.**

### **Path A: The Local Python/Node Orchestration Script (Recommended)**

You (Claude Code) will write a local orchestration script (e.g., generate\_carousel.py) that handles the API calls to Gemini.

1. **Input:** Claude Code passes a structured text layout or directly triggers the script with arguments.  
2. **Execution:** The script calls the Google GenAI SDK (google-genai library) using the local environment variable GEMINI\_API\_KEY.  
3. **Text & Image Generation:**  
   * It uses Gemini (e.g., gemini-2.5-flash or newer) to perfect the 5-10 slide micro-copy.  
   * It uses Gemini's integrated image generation capabilities (Imagen models via the Gemini API) to generate high-resolution slide backgrounds/graphics.  
4. **Storage:** The script automatically downloads the generated images and saves them alongside a slides.md file in a structured path: ./output/carousels/\[carousel\_slug\]/.

### **Path B: The Model Context Protocol (MCP) Bridge**

If the workspace supports MCP servers, we can connect Claude Code directly to an MCP server wrapper for the Google Gemini/Vertex API.

* You will be able to call Gemini tools natively inside your chat prompt (e.g., use\_tool("gemini\_generate\_image", ...)).  
* *Limitation:* Requires setting up a persistent MCP server. If this is too complex for the current workspace, default immediately to **Path A**.

## **3\. Data Architecture (The Shared Directory)**

Both you (Claude Code) and the execution script will read/write to this local directory structure. This ensures absolute sync without manual file transfers.

/my-carousel-project/  
├── .env                     \# Stores GEMINI\_API\_KEY and CLAUDE\_API\_KEY  
├── claude\_gemini\_automation\_plan.md \# This instructions file  
├── generator.py             \# The script you will write to call Gemini  
└── output/                  \# Shared storage (never manual)  
    └── \[carousel-topic-slug\]/  
        ├── metadata.json    \# JSON payload of prompts and settings  
        ├── slides.md        \# The slide-by-slide copy & instructions  
        ├── slide\_1.png      \# Background / visual for slide 1  
        ├── slide\_2.png      ...  
        └── slide\_3.png      ...

## **4\. Your Step-by-Step Implementation Instructions (For Claude Code)**

Please execute the following steps sequentially:

### **Step 1: Environment Scan**

* Check if Python or Node.js is installed in this workspace.  
* Check if a .env file exists. If not, prompt the user or create one with placeholders for GEMINI\_API\_KEY.

### **Step 2: Install SDKs**

* Install the official Google GenAI package:  
  * For Python: pip install google-genai python-dotenv  
  * For Node: npm install @google/genai dotenv

### **Step 3: Write the Generator Script (generator.py)**

Create a robust script that:

1. Reads the API key.  
2. Takes a carousel topic as an input parameter.  
3. Requests a JSON-structured response from Gemini containing:  
   * The slide text (Header, Body, Call to Action).  
   * An optimized, descriptive image prompt for each slide.  
4. Loops through the slide JSON and calls Gemini's Image Generation API to create visual assets matching each slide's visual prompt.  
5. Saves the text layout into slides.md and downloads each image to ./output/\[carousel-topic-slug\]/.

### **Step 4: Run a Test**

* Run the script with a test topic (e.g., *"How to leverage Claude Code for developer productivity"*).  
* Verify that all directories are created, the text is generated, and the images are saved successfully.  
* Report back to the user with a preview of the generated slide outline.

## **5\. First Post Best Practices to Bake into the Script**

When generating the carousel copy, enforce these constraints in your prompts to Gemini:

* **The 23-Character Rule:** The title/hook on Slide 1 must feature its most important keyword/hook in the first 23 characters to prevent being truncated or lost in small mobile feeds.  
* **Visual Continuity:** The image prompts generated for Slide 1 through Slide N must share a unified visual theme, color palette, and style (e.g., "minimalist dark-mode futuristic tech illustration, high contrast").  
* **Actionable CTA:** The final slide must have a clear single call to action (e.g., "Save this post" or "Comment 'AUTOMATE' below").

*Claude, please analyze this file and propose the immediate next command to run to initialize this automation.*