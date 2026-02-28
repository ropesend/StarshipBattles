# QA Session Observer

The QA Session Observer is a set of background Python scripts designed to passively assist you in QA testing StarshipBattles. It aligns your spoken microphone commentary with screenshots you manually capture via Windows Snipping Tool into a unified Markdown log for Agentic review.

## Setup Instructions

1. **Install Dependencies**
   Navigate to this directory and install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   Copy `.env.example` to `.env` and fill in:
   - `SCREENSHOTS_DIR`: The path the Windows Snipping Tool deposits new files into.
   - `GOOGLE_APPLICATION_CREDENTIALS`: Path to your Google Cloud Service Account JSON file. 

3. **Google Cloud Auth**
   The Service Account must have `Cloud Speech-to-Text API` permissions enabled.

   **How to get your `GOOGLE_APPLICATION_CREDENTIALS` JSON file:**
   Google AI Studio is different from Google Cloud. You need a Google Cloud account to use the Speech-to-Text API.
   1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
   2. Create a new Project (or select an existing one).
   3. In the search bar at the top, type **Cloud Speech-to-Text API** and click on it.
   4. Click **Enable** to turn the API on for your project. (Note: You may be prompted to set up billing, but it has a free tier that covers up to 60 minutes per month).
   5. Go to the Navigation Menu (hamburger icon) > **IAM & Admin** > **Service Accounts**.
   6. Click **+ CREATE SERVICE ACCOUNT** at the top.
   7. Give it a name (e.g., `qa-observer`) and click **Create and Continue**, then **Done**.
   8. In the list of service accounts, click on the one you just created.
   9. Go to the **Keys** tab at the top.
   10. Click **Add Key** > **Create new key**.
   11. Choose **JSON** and click **Create**.
   12. A `.json` file will download to your computer. Move this file to a safe location (e.g., `C:\Users\rossr\Downloads\my-project-key.json`).
   13. In your `.env` file, set `GOOGLE_APPLICATION_CREDENTIALS` to the absolute path of that file.

## Usage

### Stage 1 & 2: Record and Process
Before starting your play session, run:
```bash
python observer.py
```
This script will:
- Record continuous chunks of audio from your default microphone.
- Listen to your `SCREENSHOTS_DIR` and intercept newly created screenshots.
- Collate everything into a unique `session_data/YYYYMMDD_HHMMSS/` folder.

When your play session is finished, **hit `Ctrl+C` in the terminal to stop the observer.**

As soon as it stops, it will **automatically** run the processor stage! It will:
- Stitch all audio together using Google's Word-Level Timestamps.
- Inject your screenshots seamlessly into the spoken text.
- Generate your `QA_Session_Log.md` directly into the timestamped session folder.

---

### Stage 3: The Antigravity Agent Review

When you are ready to fix bugs or build features based on your session:

1. Copy the generated `QA_Session_Log.md` and the `images/` directory into the main StarshipBattles project folder.
2. Provide the Agent with the following prompt:

> "Review the QA_Session_Log.md file. Cross-reference the spoken feedback and the embedded screenshots with the current codebase. Break down the notes into three categories: Bug Reports, Feature Requests, and Major Projects. For bugs, identify the specific Python files likely causing the issue. For features, draft a step-by-step implementation plan."
