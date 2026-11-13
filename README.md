# Smart Parking Management System with AI
College minor-project website prototype built with Flask and SQLite.

## Run
1. Install Python 3.10+
2. `python -m venv .venv`
3. Activate it (`.venv\\Scripts\\activate` on Windows; `source .venv/bin/activate` on macOS/Linux)
4. `pip install -r requirements.txt`
5. `python app.py`
6. Open http://127.0.0.1:5000

## Pages
- `/` dashboard
- `/admin` add, toggle and deactivate parking slots
- `/presentation` project presentation slides
- `/api/status` JSON status endpoint
- `/health` health check

## Important
This package is a working DEMO using seeded sample parking data and a random status simulator. It does not connect a live camera or run YOLO inference yet. The supplied report proposes OpenCV + a YOLO-family detector, parking-region mapping, SQLite and Flask. Implement and test the camera/detector pipeline before claiming live AI functionality. Add actual screenshots, test results, student details and measured accuracy before final submission. Add authentication and replace the demo secret key before public deployment.
