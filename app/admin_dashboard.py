import streamlit as st
import pandas as pd
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, os.path.join(parent_dir, 'db'))

from database import Database

class AdminDashboard:
    """Admin dashboard for viewing and managing bookings"""
    
    def __init__(self, database: Database):
        self.database = database
    
    def render(self):
        """Render the admin dashboard"""
        st.title("📊 Admin Dashboard")
        st.markdown("---")
        
        # Summary statistics
        self.render_statistics()
        
        st.markdown("---")
        
        # Search and filter
        search_term = st.text_input("🔍 Search by name, email, or date", "")
        
        # Get bookings
        if search_term:
            bookings = self.database.search_bookings(search_term)
        else:
            bookings = self.database.get_all_bookings()
        
        # Display bookings
        if bookings:
            self.render_bookings_table(bookings)
        else:
            st.info("No bookings found.")
        
        # Refresh button
        if st.button("🔄 Refresh Data"):
            st.rerun()
    
    def render_statistics(self):
        """Render summary statistics"""
        bookings = self.database.get_all_bookings()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Bookings", len(bookings))
        
        with col2:
            confirmed = sum(1 for b in bookings if b['status'] == 'confirmed')
            st.metric("Confirmed", confirmed)
        
        with col3:
            # Count unique booking types
            booking_types = set(b['booking_type'] for b in bookings)
            st.metric("Service Types", len(booking_types))
        
        with col4:
            # Count unique customers
            customers = set(b['customer_email'] for b in bookings)
            st.metric("Unique Customers", len(customers))
    
    def render_bookings_table(self, bookings):
        """Render bookings in a table format"""
        st.subheader("📅 All Bookings")
        
        # Convert to DataFrame
        df = pd.DataFrame(bookings)
        
        # Reorder columns for better display
        column_order = [
            'booking_id', 'customer_name', 'customer_email', 
            'customer_phone', 'booking_type', 'date', 'time', 
            'status', 'created_at'
        ]
        df = df[column_order]
        
        # Rename columns for display
        df.columns = [
            'ID', 'Name', 'Email', 'Phone', 
            'Type', 'Date', 'Time', 'Status', 'Created At'
        ]
        
        # Style the dataframe
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ID": st.column_config.NumberColumn(
                    "ID",
                    help="Booking ID",
                    format="%d"
                ),
                "Status": st.column_config.TextColumn(
                    "Status",
                    help="Booking status"
                ),
                "Date": st.column_config.DateColumn(
                    "Date",
                    help="Appointment date"
                ),
                "Time": st.column_config.TimeColumn(
                    "Time",
                    help="Appointment time"
                )
            }
        )
        
        # Export functionality
        st.markdown("---")
        col1, col2 = st.columns([3, 1])
        
        with col2:
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Export to CSV",
                data=csv,
                file_name="bookings_export.csv",
                mime="text/csv"
            )
    
    def render_booking_details(self, booking_id: int):
        """Render detailed view of a specific booking"""
        booking = self.database.get_booking_by_id(booking_id)
        
        if booking:
            st.subheader(f"Booking Details - ID #{booking_id}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Customer Information**")
                st.write(f"Name: {booking['customer_name']}")
                st.write(f"Email: {booking['customer_email']}")
                st.write(f"Phone: {booking['customer_phone']}")
            
            with col2:
                st.markdown("**Appointment Details**")
                st.write(f"Type: {booking['booking_type']}")
                st.write(f"Date: {booking['date']}")
                st.write(f"Time: {booking['time']}")
                st.write(f"Status: {booking['status']}")
        else:
            st.error(f"Booking with ID {booking_id} not found.")