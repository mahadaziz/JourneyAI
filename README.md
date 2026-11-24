# JourneyAI

JourneyAI is a writing assistant for journalists exploring a dataset. A writer can inspect a statistical finding, open its chart and draft a paragraph in the same workspace. The prototype also uses selected findings and draft text to prompt a language model for hypotheses the writer can investigate.

![JourneyAI dashboard with a draft and a line chart of average city fuel consumption by model year](docs/dashboard-preview.png)

In the sample CSV, average city fuel consumption falls from 10.6 to 9.2 L/100 km between 2018 and 2023. Selecting **model year** and opening its average fuel consumption chart reproduces this view.

## Inside the dashboard

- **Explore a column.** The Flask analysis code looks for outliers, trends, distributions and associations. The React dashboard renders the results, with D3 bar, line and scatter plots for graphical findings.
- **Develop a story.** A Tiptap editor sits beside the findings. The hypothesis panel can send selected insights or writing context to a Hugging Face text-generation endpoint and record thumbs-up or thumbs-down feedback.
- **Return to a draft.** Upload a CSV, name the story and select **Save** to store its title, text and formatting in MongoDB. Open the story from your homepage to resume writing alongside the same dataset. If another tab has saved a newer revision, the editor keeps your current edits on screen and explains the conflict.

## Run locally

The frontend uses Next.js 14, React 18 and NextAuth. The backend uses Flask, pandas, SciPy, scikit-learn and PyMongo. Both services share a MongoDB database named `db`.

1. Start MongoDB locally or provide a development database. The app creates its collections on first use.
2. For a fresh checkout, copy the [frontend environment template](src/frontend/front-end/.env.example) and [backend environment template](src/backend/.env.example) to a file named `.env` beside each template. Point both connection strings at the same instance. Generate a separate private value for each signing secret using the commands in the templates.
3. For the optional hypothesis feature, set `HF_TOKEN` and, if needed, `HF_INFERENCE_URL` on the backend. The prototype originally targeted Falcon-7B-Instruct. A replacement endpoint must accept Hugging Face text-generation inputs and return a list containing `generated_text`.

**Backend.** From the repository root in PowerShell, use Python 3.11 to start Flask in one terminal.

```powershell
cd src/backend
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run.py
```

**Frontend.** In a second terminal, start Next.js using the original development baseline of Node 20.9 and npm 10.1.

```powershell
cd src/frontend/front-end
npm ci
npm run dev
```

Open the app at `http://localhost:3000`. The Flask health route at `http://127.0.0.1:8080/` returns `home`. Register a development account, sign in and upload the [synthetic vehicle CSV](examples/vehicles.csv) to open the dashboard. Select **model year** to explore how fuel consumption changes across the six years of sample data.

**Docker Compose.** To run both application services in containers, set the two MongoDB URIs to an address reachable from inside Docker. With MongoDB running on the Windows host, use `host.docker.internal` in place of `127.0.0.1` in those URIs. Keep the Flask URL browser-accessible. Run this command from the repository root after creating the two environment files.

```powershell
docker compose --env-file src/frontend/front-end/.env -f src/compose.yml up --build
```

## Check the dashboard

From `src/backend`, run the regression tests with Python 3.11. They use an in-memory MongoDB substitute to check startup, upload permissions, analysis of separate datasets, chart generation and the response when model access is unconfigured.

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests
```

To check draft saving in a browser, start both services against a disposable development database. The test creates two accounts and uploads a small CSV. It saves formatted text, signs out and back in, checks concurrent edits and verifies that a second account cannot save the first writer's draft. From `src/frontend/front-end`, run the following commands.

```powershell
npx playwright-core install chromium
npm run test:draft
```

The browser test opens `http://localhost:3000` by default. Set `JOURNEYAI_TEST_URL` for a different local port or `JOURNEYAI_BROWSER_PATH` to use an existing Chromium or Edge executable.

## Project materials

The [design document](docs/Group%208%20-%20Design%20Document.pdf) describes the components and interface. The [verification and validation report](docs/Group%208%20-%20Verification%20and%20Validation%20Document.pdf) describes how the team evaluated insights, hypotheses and writing workflows.

JourneyAI began as the McMaster University computer science capstone *Designing Assistant for Data-Driven Stories*. The team was Sarib Kashif, Leo Srayeddin, Omar Zahir, Talha Amjad and Mahad Aziz, supervised by Professor Swati Mishra.
