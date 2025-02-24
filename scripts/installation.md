## Running the Script  

To run the test script, follow these steps:  

### 1. Install Dependencies  
Make sure you have Python installed. Then, install dependencies from `backend/requirements.txt`, excluding Linux-only packages like `uvloop` if necessary:  

```bash
pip install -r backend/requirements.txt --no-binary uvloop
```

*(Omit `--no-binary uvloop` if running on Linux.)*  

### 2. Set Up Required Databases  
Ensure that **PostgreSQL** and **Redis** are installed and running. The default settings in `settings.py` use SQLite and an in-memory channel layer. If you haven't configured PostgreSQL or Redis, uncomment and modify these sections as needed.  

### 3. Run the Scripts  
Execute the following script from the project root:  

```bash
./scripts/run.sh
```

```bash
./scripts/test.sh
```