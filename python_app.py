import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(layout="wide", page_title="Sierra Fest Project Manager")

st.title("Sierra Fest Project Manager Simulation")
st.markdown("### An Interactive Project Management Learning Tool")

# Initialize session state variables
if 'game_started' not in st.session_state:
    st.session_state.game_started = False
if 'current_day' not in st.session_state:
    st.session_state.current_day = 0
if 'tasks_completed' not in st.session_state:
    st.session_state.tasks_completed = []
if 'resources_allocated' not in st.session_state:
    st.session_state.resources_allocated = {}
if 'budget_spent' not in st.session_state:
    st.session_state.budget_spent = 0
if 'random_events' not in st.session_state:
    st.session_state.random_events = []
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'team_morale' not in st.session_state:
    st.session_state.team_morale = 50  # Scale of 0-100
if 'feedback' not in st.session_state:
    st.session_state.feedback = []

# Sierra Fest WBS data
@st.cache_data
def load_wbs_data():
    # Based on the case study's WBS table
    data = {
        'WBS Code': ['1', '1.1', '1.2', '1.3', '1.4', '1.5', '2', '2.1', '2.2', '2.3', '2.4', '2.5', 
                    '3', '3.1', '3.2', '3.3', '3.4', '3.5', '4', '4.1', '4.2', '4.3', '4.4', '4.5',
                    '5', '5.1', '5.2', '5.3', '5.4', '5.5', '6', '6.1', '6.2', '6.3', '6.4', '6.5',
                    '7', '7.1', '7.2', '7.3', '7.4', '7.5', '8', '8.1', '8.2', '8.3', '8.4', '8.5',
                    '9', '9.1', '9.2', '9.3', '9.4', '9.5'],
        'Task Description': ['Event Planning and Management', 'Form Core Organizing Committee', 'Define Event Theme and Goals', 
                            'Develop Master Schedule', 'Create Detailed Budget', 'Obtain Required Permissions',
                            'Sponsorship and Finance', 'Create Sponsorship Packages', 'Form Sponsorship Teams', 
                            'Conduct Sponsor Outreach', 'Set Up Payment Collection Systems', 'Monitor Budget and Expenses',
                            'Venue and Logistics', 'Identify Venue Requirements', 'Book and Secure Campus Venues', 
                            'Arrange for Equipment and Infrastructure', 'Plan Contingency for Weather Issues', 'Finalize Layout and Setup Plans',
                            'Accommodation Management', 'Estimate Participant Numbers', 'Negotiate with Local Hotels', 
                            'Develop Alternative Accommodation Plans', 'Set Up Booking System', 'Finalize Accommodation Arrangements',
                            'Events and Programming', 'Define Event Categories', 'Develop Rules for Competitions', 
                            'Book Celebrity Performers', 'Arrange for Judges and Hosts', 'Create Detailed Event Schedules',
                            'Marketing and Promotion', 'Develop Branding and Creative Elements', 'Create Event Website and App', 
                            'Implement College Ambassador Program', 'Execute Social Media Strategy', 'Conduct Pre-event Workshops',
                            'Participant Management', 'Develop Registration Process', 'Create Participant Information Package', 
                            'Process Registrations', 'Prepare Welcome Kits', 'Manage On-site Registration',
                            'Event Execution', 'Set Up All Venues', 'Conduct Event Day 1', 'Conduct Event Day 2', 
                            'Manage Performer Logistics', 'Oversee Award Ceremonies',
                            'Post-Event Activities', 'Conduct Venue Cleanup', 'Process Financial Settlements', 
                            'Collect and Analyze Feedback', 'Create Documentation and Handover', 'Conduct Team Celebration'],
        'Duration (Days)': [180, 7, 5, 10, 7, 30, 120, 10, 5, 90, 7, 120, 100, 7, 10, 45, 15, 14, 90, 10, 30, 14, 7, 21,
                           150, 5, 14, 60, 30, 14, 120, 21, 30, 45, 90, 30, 90, 14, 14, 60, 14, 2, 2, 1, 1, 1, 2, 1,
                           30, 1, 14, 14, 21, 1],
        'Predecessors': ['', '', '1.1', '1.2', '1.2', '1.2', '', '1.4', '1.1', '2.1, 2.2', '1.4', '1.4', 
                         '', '1.3', '3.1', '3.2', '3.2', '3.3, 3.4', '', '1.2', '4.1', '4.1', '4.2, 4.3', '4.4',
                         '', '1.2', '5.1', '1.2', '5.1', '5.2, 5.3, 5.4', '', '1.2', '6.1', '6.1', '6.1', '6.1, 5.2',
                         '', '6.2', '3.5, 4.5, 5.5', '7.1', '7.2', '7.3, 7.4', '', '3.5', '8.1', '8.2', '5.3', '8.2, 8.3',
                         '', '8.3', '8.5', '8.5', '9.3', '9.2, 9.4'],
        'Resource Type': ['Management', 'Management', 'Creative', 'Planning', 'Finance', 'Administrative',
                          'Finance', 'Marketing', 'Management', 'Marketing', 'Technical', 'Finance',
                          'Logistics', 'Planning', 'Administrative', 'Technical', 'Planning', 'Design',
                          'Logistics', 'Planning', 'Negotiation', 'Planning', 'Technical', 'Administrative',
                          'Creative', 'Creative', 'Planning', 'Marketing', 'Administrative', 'Planning',
                          'Marketing', 'Creative', 'Technical', 'Marketing', 'Marketing', 'Logistics',
                          'Logistics', 'Planning', 'Creative', 'Administrative', 'Logistics', 'Logistics',
                          'Operations', 'Technical', 'Operations', 'Operations', 'Logistics', 'Administrative',
                          'Administrative', 'Logistics', 'Finance', 'Analytics', 'Administrative', 'Management'],
        'Cost (₹)': [0, 0, 0, 0, 0, 5000, 0, 2000, 0, 5000, 3000, 0, 0, 0, 0, 150000, 5000, 0,
                    0, 0, 0, 0, 2000, 0, 0, 0, 0, 300000, 20000, 0, 0, 10000, 15000, 10000, 8000, 15000,
                    0, 0, 3000, 0, 25000, 5000, 0, 50000, 100000, 100000, 30000, 10000,
                    0, 5000, 0, 3000, 0, 10000],
        'Status': ['Not Started'] * 53,
        'Level': [0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1,
                 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1,
                 0, 1, 1, 1, 1, 1]
    }
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Add additional columns for gameplay
    df['Completion'] = 0
    df['Start Day'] = None
    df['End Day'] = None
    df['Assigned To'] = None
    
    return df

wbs_df = load_wbs_data()

# Resource Management data
@st.cache_data
def load_resource_data():
    resources = {
        'Management': {'count': 3, 'efficiency': 1.0, 'cost_per_day': 1000},
        'Creative': {'count': 4, 'efficiency': 0.9, 'cost_per_day': 800},
        'Planning': {'count': 5, 'efficiency': 1.0, 'cost_per_day': 700},
        'Finance': {'count': 2, 'efficiency': 1.1, 'cost_per_day': 900},
        'Administrative': {'count': 4, 'efficiency': 0.95, 'cost_per_day': 600},
        'Marketing': {'count': 5, 'efficiency': 1.0, 'cost_per_day': 800},
        'Technical': {'count': 3, 'efficiency': 1.2, 'cost_per_day': 1200},
        'Logistics': {'count': 6, 'efficiency': 0.9, 'cost_per_day': 750},
        'Design': {'count': 2, 'efficiency': 1.1, 'cost_per_day': 950},
        'Negotiation': {'count': 2, 'efficiency': 1.0, 'cost_per_day': 1100},
        'Operations': {'count': 8, 'efficiency': 1.0, 'cost_per_day': 850},
        'Analytics': {'count': 2, 'efficiency': 1.2, 'cost_per_day': 1000}
    }
    return resources

resources = load_resource_data()

# Random events
@st.cache_data
def load_random_events():
    events = [
        {"title": "Unexpected Rain Forecast", "description": "Weather department predicts heavy rain during the festival days.", 
         "impact": "Tasks related to outdoor venues will take 50% longer.", "affected_tasks": ["3.3", "3.4", "8.1"]},
        {"title": "Major Sponsor Backs Out", "description": "A key sponsor has withdrawn their commitment due to budget constraints.", 
         "impact": "Budget reduced by ₹50,000", "affected_tasks": ["2.3"]},
        {"title": "Celebrity Artist Demands Change", "description": "The main performer wants to change their performance date.", 
         "impact": "Reschedule required, affecting event day planning", "affected_tasks": ["5.3", "8.4"]},
        {"title": "Transport Strike", "description": "Local transport union announces a strike during the festival week.", 
         "impact": "Accommodation and logistics planning must be revisited", "affected_tasks": ["4.3", "4.5", "7.2"]},
        {"title": "Social Media Campaign Goes Viral", "description": "Your promotional video has gone viral on social media!", 
         "impact": "Participant registrations increase by 30%, but requires more resources", "affected_tasks": ["7.3", "7.4", "4.5"]},
        {"title": "Budget Approval Delay", "description": "Institute administration is taking longer to approve the budget.", 
         "impact": "Financial planning tasks will be delayed by 7 days", "affected_tasks": ["1.4", "2.1", "2.4"]},
        {"title": "New Technology Sponsor", "description": "A technology company offers to sponsor and provide event management software.", 
         "impact": "Technical tasks can be completed 20% faster", "affected_tasks": ["6.2", "7.1", "7.3"]},
        {"title": "Volunteer Surge", "description": "More students than expected have volunteered to help with the event.", 
         "impact": "Logistics and operational tasks can be completed 15% faster", "affected_tasks": ["7.4", "8.1", "9.1"]}
    ]
    return events

random_events = load_random_events()

# Function to calculate critical path
def calculate_critical_path(df):
    G = nx.DiGraph()
    
    # Filter only leaf tasks (not summary tasks)
    leaf_tasks = df[~df['WBS Code'].isin(['1', '2', '3', '4', '5', '6', '7', '8', '9'])]
    
    # Add nodes
    for idx, task in leaf_tasks.iterrows():
        G.add_node(task['WBS Code'], duration=task['Duration (Days)'], desc=task['Task Description'])
    
    # Add edges based on predecessors
    for idx, task in leaf_tasks.iterrows():
        if task['Predecessors']:
            predecessors = [pred.strip() for pred in task['Predecessors'].split(',')]
            for pred in predecessors:
                if pred in G.nodes():
                    G.add_edge(pred, task['WBS Code'])
    
    # Add start and end nodes
    G.add_node('START', duration=0, desc='Project Start')
    G.add_node('END', duration=0, desc='Project End')
    
    # Connect start node to tasks with no predecessors
    for node in G.nodes():
        if node not in ['START', 'END'] and G.in_degree(node) == 0:
            G.add_edge('START', node)
    
    # Connect tasks with no successors to end node
    for node in G.nodes():
        if node not in ['START', 'END'] and G.out_degree(node) == 0:
            G.add_edge(node, 'END')
    
    # Calculate earliest start time (EST)
    est = {'START': 0}
    
    # Topological sort to calculate EST
    for node in nx.topological_sort(G):
        if node == 'START':
            continue
        
        # EST of a node is the maximum of the earliest finish times (EFT) of its predecessors
        est[node] = 0
        for pred in G.predecessors(node):
            est[node] = max(est[node], est[pred] + G.nodes[pred]['duration'])
    
    # Calculate latest start time (LST)
    lst = {}
    
    # Set LST of END node to its EST
    lst['END'] = est['END']
    
    # Reversed topological sort to calculate LST
    for node in reversed(list(nx.topological_sort(G))):
        if node == 'END':
            continue
        
        # Initialize LST of the node to a large value
        lst[node] = float('inf')
        
        # LST of a node is the minimum of the latest start times (LST) of its successors minus its duration
        for succ in G.successors(node):
            lst[node] = min(lst[node], lst[succ] - G.nodes[node]['duration'])
    
    # Calculate slack
    slack = {}
    for node in G.nodes():
        slack[node] = lst[node] - est[node]
    
    # Identify critical path (nodes with zero slack)
    critical_path = [node for node in G.nodes() if slack[node] == 0]
    
    return G, est, lst, slack, critical_path

# Game initialization
def start_game():
    st.session_state.game_started = True
    st.session_state.current_day = 0
    st.session_state.tasks_completed = []
    st.session_state.resources_allocated = {}
    st.session_state.budget_spent = 0
    st.session_state.random_events = []
    st.session_state.score = 0
    st.session_state.team_morale = 50
    st.session_state.feedback = []
    
    # Reset WBS
    global wbs_df
    wbs_df = load_wbs_data()

def end_game():
    st.session_state.game_started = False

# Sidebar content
with st.sidebar:
    st.header("Game Controls")
    
    if not st.session_state.game_started:
        st.write("Welcome to the Sierra Fest Project Manager Simulation!")
        st.write("This game will help you understand project management concepts using the Sierra Annual Fest case study.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Start Game", key="start_btn"):
                start_game()
        with col2:
            difficulty = st.selectbox("Difficulty Level", ["Easy", "Medium", "Hard"])
    else:
        st.subheader(f"Day: {st.session_state.current_day} of 180")
        st.progress(min(1.0, st.session_state.current_day / 180))
        
        # Budget information
        total_budget = 900000  # ₹9 Lakhs
        st.metric("Budget", f"₹{total_budget - st.session_state.budget_spent:,}", 
                 f"-₹{st.session_state.budget_spent:,}")
        
        # Team morale
        st.metric("Team Morale", f"{st.session_state.team_morale}/100")
        
        # Score
        st.metric("Score", st.session_state.score)
        
        # Advance time button
        days_to_advance = st.selectbox("Days to advance", [1, 3, 7, 14, 30])
        if st.button(f"Advance {days_to_advance} days", key="advance_btn"):
            for _ in range(days_to_advance):
                # Simulate one day of project progress
                # Update task completions
                for idx, task in wbs_df.iterrows():
                    if task['Status'] == 'In Progress':
                        # Check if task is finished
                        if task['Completion'] >= 100:
                            wbs_df.at[idx, 'Status'] = 'Completed'
                            wbs_df.at[idx, 'End Day'] = st.session_state.current_day
                            st.session_state.tasks_completed.append(task['WBS Code'])
                            st.session_state.feedback.append(f"🎉 Task '{task['Task Description']}' completed!")
                            st.session_state.score += 10
                            st.session_state.team_morale = min(100, st.session_state.team_morale + 2)
                        else:
                            # Progress based on resources assigned
                            resource_type = task['Resource Type']
                            if task['WBS Code'] in st.session_state.resources_allocated:
                                resources_assigned = st.session_state.resources_allocated[task['WBS Code']]
                                efficiency = resources[resource_type]['efficiency']
                                progress_per_day = (resources_assigned / task['Duration (Days)']) * 100 * efficiency
                                wbs_df.at[idx, 'Completion'] += progress_per_day
                                
                                # Add resource cost to budget
                                cost_per_day = resources[resource_type]['cost_per_day'] * resources_assigned
                                st.session_state.budget_spent += cost_per_day
            
                # Trigger random events occasionally
                if st.session_state.current_day % 15 == 0 and len(random_events) > 0:
                    # Select random event
                    event_index = np.random.randint(0, len(random_events))
                    event = random_events[event_index]
                    st.session_state.random_events.append(event)
                    st.session_state.feedback.append(f"⚠️ EVENT: {event['title']} - {event['description']}")
                    
                    # Apply event effects
                    if "Budget reduced" in event['impact']:
                        st.session_state.budget_spent += 50000
                        st.session_state.team_morale = max(0, st.session_state.team_morale - 10)
                    elif "faster" in event['impact']:
                        st.session_state.team_morale = min(100, st.session_state.team_morale + 5)
                    elif "longer" in event['impact'] or "delay" in event['impact']:
                        st.session_state.team_morale = max(0, st.session_state.team_morale - 5)
                
                # Increment day
                st.session_state.current_day += 1
                
                # Check for game end
                if st.session_state.current_day >= 180:
                    # Calculate final score
                    completed_tasks = len(st.session_state.tasks_completed)
                    completion_percentage = completed_tasks / len(wbs_df[~wbs_df['WBS Code'].isin(['1', '2', '3', '4', '5', '6', '7', '8', '9'])])
                    budget_percentage = st.session_state.budget_spent / total_budget
                    
                    final_score = (completion_percentage * 0.7 + (1 - budget_percentage) * 0.3) * 1000
                    st.session_state.score = int(final_score)
                    
                    st.session_state.feedback.append(f"🏁 Game Over! Final Score: {st.session_state.score}")
                    break

        if st.button("End Game", key="end_btn"):
            end_game()

# Main content
if not st.session_state.game_started:
    st.title("Sierra Fest Project Manager")
    st.image("https://images.unsplash.com/photo-1540317580384-e5d43867caa6?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80", 
             caption="College Festival Management Simulation")
    
    st.markdown("""
    ### Learning Objectives:
    - Understand the concept of Work Breakdown Structure (WBS)
    - Learn about task dependencies and critical path analysis
    - Practice resource allocation and budget management
    - Experience project management challenges in a real-world context
    - Develop decision-making skills for handling unexpected events

    ### Game Mechanics:
    1. Allocate resources to tasks
    2. Monitor task progress and dependencies
    3. Manage budget constraints
    4. React to unexpected events
    5. Balance time, scope, and cost to achieve the best possible outcome

    ### Based on the Sierra Annual Fest Case Study
    This simulation is based on a real college festival organized in a remote location, 
    facing unique challenges in sponsorship, accommodation, and promotion.

    **Click "Start Game" in the sidebar to begin!**
    """)

    # Display the WBS
    st.subheader("Work Breakdown Structure (WBS)")
    st.dataframe(wbs_df[['WBS Code', 'Task Description', 'Duration (Days)', 'Predecessors', 'Resource Type', 'Cost (₹)']])

else:
    st.title(f"Sierra Fest Project Manager - Day {st.session_state.current_day}")
    
    # Tabs for different game views
    tab1, tab2, tab3, tab4 = st.tabs(["Tasks", "Resources", "Critical Path", "Events & Feedback"])
    
    with tab1:
        st.subheader("Task Management")
        
        # Filter tasks based on status
        task_status = st.multiselect("Filter by Status", 
                                    ["Not Started", "In Progress", "Completed", "Blocked"], 
                                    default=["Not Started", "In Progress"])
        
        filtered_df = wbs_df[wbs_df['Status'].isin(task_status)]
        
        # Show tasks that can be started (all predecessors completed)
        def can_start_task(task):
            if task['Status'] != 'Not Started':
                return False
                
            if not task['Predecessors']:
                return True
                
            predecessors = [pred.strip() for pred in task['Predecessors'].split(',')]
            return all(pred in st.session_state.tasks_completed for pred in predecessors)
        
        startable_tasks = wbs_df[wbs_df.apply(can_start_task, axis=1)]
        
        if not startable_tasks.empty:
            st.success(f"You have {len(startable_tasks)} tasks that can be started now!")
            
            # Allow starting new tasks
            st.subheader("Start New Tasks")
            for idx, task in startable_tasks.iterrows():
                cols = st.columns([3, 1, 1, 1])
                with cols[0]:
                    st.write(f"{task['WBS Code']}: {task['Task Description']}")
                with cols[1]:
                    st.write(f"Duration: {task['Duration (Days)']} days")
                with cols[2]:
                    st.write(f"Type: {task['Resource Type']}")
                with cols[3]:
                    resource_type = task['Resource Type']
                    max_resources = resources[resource_type]['count']
                    
                    # Allocate resources to task
                    allocated = st.number_input(f"Allocate resources", 
                                               min_value=1, max_value=max_resources,
                                               value=1, key=f"resource_{task['WBS Code']}")
                    
                    if st.button("Start Task", key=f"start_{task['WBS Code']}"):
                        wbs_df.at[idx, 'Status'] = 'In Progress'
                        wbs_df.at[idx, 'Start Day'] = st.session_state.current_day
                        wbs_df.at[idx, 'Assigned To'] = resource_type
                        st.session_state.resources_allocated[task['WBS Code']] = allocated
                        st.session_state.feedback.append(f"🚀 Started task: {task['Task Description']}")
                        st.experimental_rerun()
        
        # Display in-progress tasks
        in_progress = wbs_df[wbs_df['Status'] == 'In Progress']
        if not in_progress.empty:
            st.subheader("Tasks In Progress")
            
            for idx, task in in_progress.iterrows():
                cols = st.columns([3, 2, 1])
                with cols[0]:
                    st.write(f"{task['WBS Code']}: {task['Task Description']}")
                with cols[1]:
                    st.progress(min(1.0, task['Completion'] / 100))
                with cols[2]:
                    st.write(f"{int(task['Completion'])}% complete")
        
        # Display task table
        st.subheader("All Tasks")
        st.dataframe(filtered_df[['WBS Code', 'Task Description', 'Duration (Days)', 
                                 'Status', 'Completion', 'Start Day', 'End Day', 'Resource Type']])
    
    with tab2:
        st.subheader("Resource Management")
        
        # Resource allocation overview
        resource_usage = {resource: 0 for resource in resources.keys()}
        
        for task_id, allocated in st.session_state.resources_allocated.items():
            task_row = wbs_df[wbs_df['WBS Code'] == task_id]
            if not task_row.empty and task_row.iloc[0]['Status'] == 'In Progress':
                resource_type = task_row.iloc[0]['Resource Type']
                resource_usage[resource_type] += allocated
        
        # Display resource usage
        st.subheader("Resource Allocation")
        
        for resource_type, details in resources.items():
            cols = st.columns([3, 1, 1, 1])
            with cols[0]:
                st.write(f"{resource_type} Team")
            with cols[1]:
                st.write(f"Available: {details['count']}")
            with cols[2]:
                st.write(f"Allocated: {resource_usage[resource_type]}")
            with cols[3]:
                st.write(f"Remaining: {details['count'] - resource_usage[resource_type]}")
                
            # Show progress bar for resource usage
            st.progress(min(1.0, resource_usage[resource_type] / details['count']))
        
        # Resource cost information
        st.subheader("Resource Costs")
        
        resource_cost_data = {
            'Resource Type': [],
            'Daily Rate (₹)': [],
            'Efficiency': []
        }
        
        for resource_type, details in resources.items():
            resource_cost_data['Resource Type'].append(resource_type)
            resource_cost_data['Daily Rate (₹)'].append(details['cost_per_day'])
            resource_cost_data['Efficiency'].append(f"{details['efficiency']:.2f}x")
        
        st.dataframe(pd.DataFrame(resource_cost_data))
    
    with tab3:
        st.subheader("Critical Path Analysis")
        
        # Calculate and display critical path
        G, est, lst, slack, critical_path = calculate_critical_path(wbs_df)
        
        st.write(f"Critical Path Tasks: {', '.join(critical_path)}")
        
        # Create a dataframe for the critical path information
        critical_path_df = pd.DataFrame({
            'Task': [node for node in G.nodes() if node not in ['START', 'END']],
            'Description': [G.nodes[node]['desc'] if node not in ['START', 'END'] else node for node in G.nodes() if node not in ['START', 'END']],
            'Duration': [G.nodes[node]['duration'] for node in G.nodes() if node not in ['START', 'END']],
            'Early Start': [est[node] for node in G.nodes() if node not in ['START', 'END']],
            'Late Start': [lst[node] for node in G.nodes() if node not in ['START', 'END']],
            'Slack': [slack[node] for node in G.nodes() if node not in ['START', 'END']],
            'On Critical Path': [node in critical_path for node in G.nodes() if node not in ['START', 'END']]
        })
        
        # Sort by early start
        critical_path_df = critical_path_df.sort_values('Early Start')
        
        # Display the critical path information
        st.dataframe(critical_path_df)
        
        # Visualize the network diagram
        st.subheader("Network Diagram")
        
        # Use a different layout depending on the network size
        layout = nx.kamada_kawai_layout(G) if len(G) < 20 else nx.shell_layout(G)
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Draw nodes
        nx.draw_networkx_nodes(G, layout, 
                              node_color=['red' if node in critical_path else 'lightblue' for node in G.nodes()],
                              node_size=500, ax=ax)
        
        # Draw edges
        nx.draw_networkx_edges(G, layout, arrows=True, ax=ax)
        
        # Draw labels
        nx.draw_networkx_labels(G, layout, font_size=8, ax=ax)
        
        st.pyplot(fig)
    
    with tab4:
        st.subheader("Events & Feedback")
        
        # Display random events
        if st.session_state.random_events:
            st.subheader("Recent Events")
            for event in st.session_state.random_events[-3:]:
                st.info(f"**{event['title']}**: {event['description']} - Impact: {event['impact']}")
        
        # Display feedback messages
        st.subheader("Game Feedback")
        for message in st.session_state.feedback[-10:]:
            st.write(message)

# Classroom Discussion Questions (shown at the bottom)
if st.session_state.game_started:
    with st.expander("Classroom Discussion Questions"):
        st.markdown("""
        ### Questions for Students:

        1. **Critical Path Analysis:**
           - How does identifying the critical path help in managing project schedules?
           - What strategies would you use to shorten the critical path in this project?

        2. **Resource Allocation:**
           - What factors should be considered when allocating resources to tasks?
           - How does resource allocation affect the duration and cost of tasks?

        3. **Risk Management:**
           - How do random events in the simulation mirror real-world project risks?
           - What risk mitigation strategies could be implemented for Sierra Fest?

        4. **Budget Management:**
           - How does the simulation demonstrate the relationship between scope, time, and cost?
           - What budget optimization strategies would you recommend?

        5. **Project Scheduling:**
           - How important are task dependencies in project planning?
           - How would you handle scheduling conflicts that arise during the project?

        6. **Remote Location Challenges:**
           - What specific challenges does the remote location of Paonta Sahib create for the festival?
           - How would you modify your project management approach for remote locations?
        """)
