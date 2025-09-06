import streamlit as st
from fuzzywuzzy import fuzz

# ---------------- Title ----------------
st.title("Welcome to Skillex!")

# ---------------- Default users (in-memory, but stored in session) ----------------
if "users" not in st.session_state:
    st.session_state.users = [
        {
            "id": "u1",
            "name": "Riri",
            "skills_have": {"Python Basics": 30, "Public Speaking": 20},
            "skills_want": ["UI Design", "Data Visualization", "DSA in C"],
            "credits": 30,
            "about": "Passionate about teaching coding and communication skills.",
            "degree": "BTech in Computer Science",
            "contact": ["riri@example.com", "github.com/riri", "linkedin.com/in/riri"],
            "upvotes": 0
        },
        {
            "id": "u2",
            "name": "Alice",
            "skills_have": {"UI Design": 40, "Figma": 30},
            "skills_want": ["Python Basics"],
            "credits": 40,
            "about": "UI/UX designer with 2 years of experience.",
            "degree": "Bachelor of Design",
            "contact": ["alice@example.com", "github.com/alice", "linkedin.com/in/alice"],
            "upvotes": 0
        },
        {
            "id": "u3",
            "name": "Bob",
            "skills_have": {"DSA in C": 50, "Java": 40},
            "skills_want": ["Public Speaking", "UI Design"],
            "credits": 20,
            "about": "Love problem-solving and teaching DSA.",
            "degree": "BSc in Computer Science",
            "contact": ["bob@example.com", "github.com/bob", "linkedin.com/in/bob"],
            "upvotes": 0
        }
    ]

users = st.session_state.users  # always work from session state

# ---------------- Track votes ----------------
if "votes" not in st.session_state:
    st.session_state.votes = {}  # {voter_id: set(of user_ids already upvoted)}

# ---------------- Session state for login flow ----------------
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "step" not in st.session_state:
    st.session_state.step = "login"


# ---------------- Helper: handle upvotes ----------------
def handle_upvote(voter_id, target_user):
    """Allow only one upvote per target per voter"""
    if voter_id == target_user["id"]:
        st.warning("You cannot upvote yourself!")
        return

    if voter_id not in st.session_state.votes:
        st.session_state.votes[voter_id] = set()

    if target_user["id"] in st.session_state.votes[voter_id]:
        st.info(f"You already upvoted {target_user['name']}.")
    else:
        target_user["upvotes"] += 1
        st.session_state.votes[voter_id].add(target_user["id"])
        st.rerun()


# ---------------- Step 1: Login/Register ----------------
if st.session_state.step == "login":
    st.subheader("Login or Register")
    with st.form("login_form"):
        login_id = st.text_input("Enter your user ID").strip()
        login_button = st.form_submit_button("Login")
        if login_button:
            user = next((u for u in users if u["id"] == login_id), None)
            if user:
                st.session_state.current_user = user
                st.session_state.step = "search"
                st.rerun()
            else:
                st.error("User ID not found. Please register.")

    st.write("--- OR ---")
    with st.form("register_form"):
        new_id = st.text_input("Choose a unique ID")
        new_name = st.text_input("Your name")
        new_skills_have = st.text_area("Skills you can teach (comma separated)")
        new_credits_for_skills = st.text_area("Credits for each skill (comma separated, same order)")
        new_skills_want = st.text_area("Skills you want to learn (comma separated)")
        new_about = st.text_area("Describe yourself")
        new_degree = st.text_area("Degrees or accomplishments relevant to your skills")
        new_contact = st.text_area("Email, GitHub, LinkedIn (comma separated)")
        register_button = st.form_submit_button("Register")
        if register_button:
            if any(u["id"] == new_id.strip() for u in users):
                st.error("This ID is already taken. Choose a different ID.")
            else:
                skills = [s.strip() for s in new_skills_have.split(",") if s.strip()]
                credits_list = [int(c.strip()) for c in new_credits_for_skills.split(",") if c.strip()]
                if len(skills) != len(credits_list):
                    st.error("Number of skills and credits must match!")
                else:
                    skills_dict = {skill: credit for skill, credit in zip(skills, credits_list)}
                    new_user = {
                        "id": new_id.strip(),
                        "name": new_name.strip(),
                        "skills_have": skills_dict,
                        "skills_want": [s.strip() for s in new_skills_want.split(",") if s.strip()],
                        "credits": 100,
                        "about": new_about.strip(),
                        "degree": new_degree.strip(),
                        "contact": [c.strip() for c in new_contact.split(",") if c.strip()],
                        "upvotes": 0
                    }
                    users.append(new_user)
                    st.session_state.current_user = new_user
                    st.session_state.step = "search"
                    st.rerun()

# ---------------- Step 2: Search & Exchange ----------------
elif st.session_state.step == "search":
    current_user = st.session_state.current_user
    st.subheader(f"Welcome {current_user['name']}! Your credits: {current_user['credits']}")

    # --- Find teachers ---
    st.subheader("Find teachers for a skill you want to learn")
    skill_to_learn_input = st.text_input("Type a skill you want to learn:").strip().lower()
    if skill_to_learn_input:
        teachers = []
        for user in users:
            if user["id"] == current_user["id"]:
                continue
            for skill, credit in user["skills_have"].items():
                if fuzz.partial_ratio(skill_to_learn_input, skill.lower()) >= 70:
                    teachers.append({'user': user, 'skill_name': skill, 'credit_value': credit})

        if teachers:
            st.write(f"People who can teach {skill_to_learn_input}:")
            for t in teachers:
                st.write(
                    f"- {t['user']['name']} teaches {t['skill_name']} "
                    f"for {t['credit_value']} credits | Upvotes: {t['user']['upvotes']}"
                )
                if st.button(f" Upvote {t['user']['name']}", key=f"upvote_t_{t['user']['id']}"):
                    handle_upvote(current_user["id"], t['user'])
                if st.button(f"Show {t['user']['name']}'s Profile", key=f"profile_t_{t['user']['id']}"):
                    st.write(f"**About:** {t['user'].get('about','Not provided')}")
                    st.write(f"**Degrees:** {t['user'].get('degree','Not provided')}")
                    contact_info = t['user'].get("contact", [])
                    if isinstance(contact_info, list) and len(contact_info) == 3:
                        st.write(f"**Email:** {contact_info[0]}")
                        st.write(f"**GitHub:** {contact_info[1]}")
                        st.write(f"**LinkedIn:** {contact_info[2]}")

    # --- Find learners ---
    st.subheader("Find learners for a skill you can teach")
    skill_to_teach_input = st.text_input("Type a skill you can teach:").strip().lower()
    if skill_to_teach_input:
        learners = []
        for user in users:
            if user["id"] == current_user["id"]:
                continue
            if any(fuzz.partial_ratio(skill_to_teach_input, s.lower()) >= 70 for s in user["skills_want"]):
                learners.append(user)
        if learners:
            st.write(f"People who want to learn {skill_to_teach_input}:")
            for l in learners:
                st.write(f"- {l['name']} (Credits: {l['credits']}) | Upvotes: {l['upvotes']}")
                if st.button(f"👍 Upvote {l['name']}", key=f"upvote_l_{l['id']}"):
                    handle_upvote(current_user["id"], l)
                if st.button(f"Show {l['name']}'s Profile", key=f"profile_l_{l['id']}"):
                    st.write(f"**About:** {l.get('about','Not provided')}")
                    st.write(f"**Degrees:** {l.get('degree','Not provided')}")
                    contact_info = l.get("contact", [])
                    if isinstance(contact_info, list) and len(contact_info) == 3:
                        st.write(f"**Email:** {contact_info[0]}")
                        st.write(f"**GitHub:** {contact_info[1]}")
                        st.write(f"**LinkedIn:** {contact_info[2]}")

    # --- Double coincidence ---
    st.subheader("Search for double coincidence")
    if st.button("Double coincidence"):
        found = False
        for i in users:
            if i["id"] == current_user["id"]:
                continue
            sh_lower = [j.lower() for j in i["skills_have"].keys()]
            sw_lower = [j.lower() for j in i["skills_want"]]
            if skill_to_learn_input and skill_to_teach_input:
                if any(fuzz.partial_ratio(skill_to_learn_input, skill) >= 70 for skill in sh_lower) and \
                   any(fuzz.partial_ratio(skill_to_teach_input, skill) >= 70 for skill in sw_lower):
                    st.write(
                        f"- **{i['name']}** can teach you **{skill_to_learn_input}** "
                        f"and wants to learn **{skill_to_teach_input}** from you. | Upvotes: {i['upvotes']}"
                    )
                    found = True
                    if st.button(f"Upvote {i['name']}", key=f"upvote_d_{i['id']}"):
                        handle_upvote(current_user["id"], i)
                    if st.button(f"Show {i['name']}'s Profile", key=f"profile_d_{i['id']}"):
                        st.write(f"**About:** {i.get('about','Not provided')}")
                        st.write(f"**Degrees:** {i.get('degree','Not provided')}")
                        contact_info = i.get("contact", [])
                        if isinstance(contact_info, list) and len(contact_info) == 3:
                            st.write(f"**Email:** {contact_info[0]}")
                            st.write(f"**GitHub:** {contact_info[1]}")
                            st.write(f"**LinkedIn:** {contact_info[2]}")
        if not found:
            st.write("No double coincidences yet. 🧐")

