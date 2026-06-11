# app.py
from layers.data_storage import AGENTS_FILE

def render_admin():
    st.header("🔑 Admin Approval Console")
    # Now using the variable instead of a hardcoded string
    if os.path.exists(AGENTS_FILE):
        df = pd.read_csv(AGENTS_FILE, ...)