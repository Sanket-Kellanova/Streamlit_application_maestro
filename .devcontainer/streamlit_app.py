import streamlit as st 
import torch
import numpy as np
from snowflake.snowpark.context import get_active_session
from PIL import Image  # To handle image processing (optional but recommended)

# Load and display an image below the imports
image_path = "mahiruhi.jpeg"  # Replace with the actual path to your image
image = Image.open(image_path)

# Resize the image if it's too large
max_width, max_height = 400, 600
image = image.resize((max_width, max_height), Image.Resampling.LANCZOS)
st.image(image, caption="Sanket and Kashmira", use_column_width=True)

# Custom CSS for large green dot and red triangle
st.markdown(
    """
    <style>
    .veg-dot {
        display: inline-block;
        width: 20px;
        height: 20px;
        background-color: green;
        border-radius: 50%;
        margin-right: 10px;
    }
    .non-veg-triangle {
        display: inline-block;
        width: 0;
        height: 0;
        border-left: 10px solid transparent;
        border-right: 10px solid transparent;
        border-bottom: 20px solid red;
        margin-right: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Render the header
st.title("Sanket Weds Kashmira :ring:")
st.write(
    """Welcoming you all to our wedding!
       I, Sanket, and my better half Kashmira (or Sameera),
       invite you to join us in this joyous moment as we begin
       our journey together.
    """
)

# Get the Snowflake session
session = get_active_session()


# Collect guest details
fn = st.text_input('Primary Guest Name (with Surname)').upper()
mob = st.text_input('Enter Mobile Number Registered Earlier')
rdc = st.selectbox('Number of Guests:', ('1', '2', '3', '4'))


# Multiselect options with icons
options = {
    "Veg": "Veg",       # Label for Veg
    "Non-Veg": "Non-Veg"  # Label for Non-Veg
}

# Multiselect widget
st.write("Please choose your cuisine preferences:")
pref = st.multiselect(
    "",
    options=list(options.keys()),
    default=["Veg"],
    format_func=lambda x: x,  # Show plain text in the selection dropdown
)

# Display selected preferences with proper HTML rendering
st.write("Selected Food Preferences:")
for p in pref:
    if p == "Veg":
        st.markdown('<span class="veg-dot"></span> Veg', unsafe_allow_html=True)
    elif p == "Non-Veg":
        st.markdown('<span class="non-veg-triangle"></span> Non-Veg', unsafe_allow_html=True)


# Process form submission
if st.button('Submit'):
    # Validate inputs
    if not mob.isdigit() or len(mob) != 10:
        st.error("Please enter a valid 10-digit mobile number.")
        st.stop()

    if not fn:
        st.error("Primary Guest Name cannot be empty.")
        st.stop()

    try:
        # Delete existing record
        del_records = """
        DELETE FROM mahiruhi.wedding.wedding_accounts 
        WHERE PRIMARY_GUEST_NAME = ? AND MOBILE = ?
        """
        session.sql(del_records, [fn, mob]).collect()

        # Insert new record
        food_pref = "Both" if len(pref) == 2 else pref[0]
        sql_insert = """
        INSERT INTO mahiruhi.wedding.wedding_accounts (primary_guest_name, guest_count, food_pref, mobile)
        VALUES (?, ?, ?, ?)
        """
        session.sql(sql_insert, [fn, rdc, food_pref, mob]).collect()

        # Display success message
        st.success("Details successfully submitted.")
        st.write(f"Name: {fn}")
        st.write(f"Number of Guests: {rdc}")
        
        # Render selected food preferences
        st.write("Food Preferences:")
        for p in pref:
            if p == "Veg":
                st.markdown('<span class="veg-dot"></span> Veg', unsafe_allow_html=True)
            elif p == "Non-Veg":
                st.markdown('<span class="non-veg-triangle"></span> Non-Veg', unsafe_allow_html=True)

        # Masked mobile number for privacy
        masked_mob = mob[:2] + "******" + mob[-2:]
        st.write(f"Mobile: {masked_mob}")
    except Exception as e:
        st.error(f"An error occurred: {e}")
