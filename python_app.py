# Sierra Annual Fest Resource Allocation Simulation
# Main application structure

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
from datetime import datetime, timedelta

# Set page config
st.set_page_config(
    page_title="Sierra Fest Resource Allocation Simulation",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----- DATA STRUCTURES -----

# WBS tasks from the case study
@st.cache_data
def load_wbs_data():
    # This would be populated with all WBS tasks from the case study
    wbs_data = {
        'WBS Code': ['1.1', '1.2', '1.3', '1.4', '1.5', '2.1', '2.2', '2.3', '2.4', '2.5', '3.1', '3.2', '3.3', '3.4', '3.5'],
        'Task Description': ['Form Core Organizing Committee', 'Define Event Theme and Goals', 'Develop Master Schedule', 
                            'Create Detailed Budget', 'Obtain Required Permissions', 'Create Sponsorship Packages', 
                            'Form Sponsorship Teams', 'Conduct Sponsor Outreach', 'Set Up Payment Collection Systems', 
                            'Monitor Budget and Expenses', 'Identify Venue Requirements', 'Book and Secure Campus Venues',
                            'Arrange for Equipment and Infrastructure', 'Plan Contingency for Weather Issues', 
                            'Finalize Layout and Setup Plans'],
        'Duration (Days)': [7, 5, 10, 7, 30, 10, 5, 90, 7, 120, 7, 10, 45, 15, 14],
        'Predecessors': ['', '1.1', '1.2', '1.2', '1.2', '1.4', '1.1', '2.1, 2.2', '1.4', '1.4', '1.3', '3.1', '3.2', '3.2', '3.3, 3.4'],
        'Min Resource Req': [2, 3, 2, 2, 1, 2, 3, 8, 1, 1, 2, 1, 5, 2, 3],
        'Base Cost': [5000, 3000, 2000, 2000, 5000, 3000, 2000, 25000, 5000, 3000, 1000, 10000, 50000, 5000, 3000]
    }
    return pd.DataFrame(wbs_data)

# Resource types and constraints
resource_types = {
    'Team Members': {'total': 25, 'cost_per_unit': 500},  # Cost per person per day
    'Budget (₹)': {'total': 500000, 'allocation': 0},
    'Equipment Sets': {'total': 10, 'cost_per_unit': 2000}  # Cost per set per day
}

# Random events that can occur
random_events = [
    {'name': 'Sponsorship Windfall', 'description': 'A major company unexpectedly offers sponsorship', 'impact': {'Budget (₹)': 50000}},
    {'name': 'Team Member Illness', 'description': 'Several team members fall ill', 'impact': {'Team Members': -3}},
    {'name': 'Weather Alert', 'description': 'Forecasted rain requires additional preparations', 'impact': {'Budget (₹)': -15000, 'Equipment Sets': -2}},
    {'name': 'Venue Issue', 'description': 'Primary venue requires maintenance', 'impact': {'Budget (₹)': -20000}},
    {'name': 'Marketing Opportunity', 'description': 'Chance to promote on local radio', 'impact': {'Budget (₹)': -10000, 'Team Members': -1}}
]

# ----- SIMULATION ENGINE -----

class FestivalSimulation:
    def __init__(self, wbs_data, resources):
        self.wbs = wbs_data
        self.resources = resources
        self.current_day = 0
        self.max_days = 180
        self.completed_tasks = []
        self.active_tasks = []
        self.resource_history = []
        self.events_occurred = []
        self.quality_score = 100
        self.participant_satisfaction = 100
        
    def allocate_resources(self, task_id, resources_allocated):
        # Logic to allocate resources to a task
        pass
        
    def advance_day(self):
        # Move simulation forward one day
        self.current_day += 1
        
        # Check for random events (20% chance each day)
        if random.random() < 0.2:
            self.trigger_random_event()
        
        # Update task progress
        self.update_tasks()
        
        # Record resource state
        self.record_resource_state()
        
    def trigger_random_event(self):
        # Select and apply a random event
        event = random.choice(random_events)
        self.events_occurred.append({'day': self.current_day, 'event': event})
        
        # Apply impacts
        for resource, impact in event['impact'].items():
            self.resources[resource]['total'] += impact
    
    def update_tasks(self):
        # Update progress on active tasks
        pass
    
    def record_resource_state(self):
        # Record the state of resources for reporting
        state = {'day': self.current_day}
        for resource, details in self.resources.items():
            state[resource] = details['total']
        self.resource_history.append(state)
    
    def get_status_report(self):
        # Generate a status report of the simulation
        return {
            'day': self.current_day,
            'resources': self.resources,
            'completed': len(self.completed_tasks),
            'active': len(self.active_tasks),
            'quality': self.quality_score,
            'satisfaction': self.participant_satisfaction,
            'events': self.events_occurred
        }

# ----- STREAMLIT UI -----

st.title("Sierra Annual Fest - Resource Allocation Simulation")

# Initialize session state
if 'simulation' not in st.session_state:
    wbs_data = load_wbs_data()
    st.session_state.simulation = FestivalSimulation(wbs_data, resource_types.copy())
    st.session_state.started = False
    st.session_state.paused = False

# Sidebar for controls
with st.sidebar:
    st.header("Simulation Controls")
    
    if not st.session_state.started:
        if st.button("Start Simulation"):
            st.session_state.started = True
    else:
        if st.session_state.paused:
            if st.button("Resume Simulation"):
                st.session_state.paused = False
        else:
            if st.button("Pause Simulation"):
                st.session_state.paused = True
    
    if st.button("Reset Simulation"):
        wbs_data = load_wbs_data()
        st.session_state.simulation = FestivalSimulation(wbs_data, resource_types.copy())
        st.session_state.started = False
        st.session_state.paused = False
    
    st.header("Resource Allocation")
    st.write("Allocate your resources to WBS tasks:")
    
    # Display current resource levels
    st.subheader("Available Resources:")
    for resource, details in st.session_state.simulation.resources.items():
        st.write(f"{resource}: {details['total']}")

# Main content area - split into two columns
col1, col2 = st.columns([3, 2])

with col1:
    st.header("WBS Tasks")
    
    # Display WBS table with resource allocation inputs
    task_data = st.session_state.simulation.wbs.copy()
    
    # Add resource allocation columns dynamically
    for i, row in task_data.iterrows():
        st.subheader(f"{row['WBS Code']}: {row['Task Description']}")
        
        # Only show allocation controls for tasks that can be started
        predecessors_completed = True
        if row['Predecessors']:
            for pred in row['Predecessors'].split(', '):
                if pred not in st.session_state.simulation.completed_tasks:
                    predecessors_completed = False
                    
        if predecessors_completed and row['WBS Code'] not in st.session_state.simulation.completed_tasks:
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                st.number_input(f"Team Members for {row['WBS Code']}", 
                               min_value=0, 
                               max_value=st.session_state.simulation.resources['Team Members']['total'],
                               key=f"team_{row['WBS Code']}")
                
            with col_b:
                st.number_input(f"Budget for {row['WBS Code']} (₹)", 
                               min_value=0, 
                               max_value=st.session_state.simulation.resources['Budget (₹)']['total'],
                               step=1000,
                               key=f"budget_{row['WBS Code']}")
                
            with col_c:
                st.number_input(f"Equipment for {row['WBS Code']}", 
                               min_value=0, 
                               max_value=st.session_state.simulation.resources['Equipment Sets']['total'],
                               key=f"equip_{row['WBS Code']}")
                
            if st.button(f"Allocate Resources to {row['WBS Code']}"):
                # Implement resource allocation logic
                pass
        elif row['WBS Code'] in st.session_state.simulation.completed_tasks:
            st.success("Task Completed!")
        else:
            st.warning("Prerequisites not completed yet")

with col2:
    st.header("Simulation Status")
    
    # Get current simulation status
    status = st.session_state.simulation.get_status_report()
    
    # Display timeline
    st.subheader("Timeline")
    st.write(f"Current Day: {status['day']} of 180")
    st.progress(status['day']/180)
    
    # Display resource usage over time (chart)
    st.subheader("Resource Utilization")
    if len(st.session_state.simulation.resource_history) > 0:
        resource_df = pd.DataFrame(st.session_state.simulation.resource_history)
        st.line_chart(resource_df.set_index('day'))
    
    # Display quality and satisfaction meters
    st.subheader("Performance Metrics")
    col_qual, col_sat = st.columns(2)
    
    with col_qual:
        st.metric("Quality Score", f"{status['quality']}/100")
        
    with col_sat:
        st.metric("Participant Satisfaction", f"{status['satisfaction']}/100")
    
    # Recent events log
    st.subheader("Recent Events")
    for event in reversed(status['events'][-5:]):
        st.info(f"Day {event['day']}: {event['event']['name']} - {event['event']['description']}")
        
    # Advance simulation automatically if running
    if st.session_state.started and not st.session_state.paused:
        # Add some delay to make it visually comprehensible
        time.sleep(0.5)
        st.session_state.simulation.advance_day()
        st.experimental_rerun()

# ----- FEEDBACK AND SCORING -----
st.header("Simulation Results")

if st.session_state.simulation.current_day >= st.session_state.simulation.max_days:
    st.balloons()
    
    # Calculate final score
    final_score = (
        st.session_state.simulation.quality_score * 0.4 + 
        st.session_state.simulation.participant_satisfaction * 0.4 +
        (st.session_state.simulation.resources['Budget (₹)']['total'] / 500000) * 100 * 0.2
    )
    
    st.success(f"Simulation Complete! Final Score: {final_score:.2f}/100")
    
    # Provide feedback based on score
    if final_score >= 90:
        st.write("Outstanding! You've masterfully balanced resources and delivered an exceptional festival.")
    elif final_score >= 75:
        st.write("Great job! Your resource allocation was effective with room for minor improvements.")
    elif final_score >= 60:
        st.write("Good effort! You completed the festival but could improve your resource efficiency.")
    else:
        st.write("You've completed the festival, but your resource allocation needs significant improvement.")
