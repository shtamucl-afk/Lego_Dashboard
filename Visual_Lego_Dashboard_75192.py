import streamlit as st
import pandas as pd
import os
import re

# Load inventory data
df = pd.read_excel("UCS_Falcon_Inventory_With_Images.xlsx")

# Assign part categories based on Element Name
def categorize(name):
    name = str(name).lower()
    if "brick" in name:
        return "Brick"
    elif "plate" in name:
        return "Plate"
    elif "tile" in name:
        return "Tile"
    elif "slope" in name:
        return "Slope"
    elif "technic" in name:
        return "Technic"
    else:
        return "Other"

# Extract part dimensions from Element Name
def extract_dimensions(name):
    match = re.search(r"\d+\s?[xX]\s?\d+", str(name))
    return match.group(0) if match else ""

df["Category"] = df["Element Name"].apply(categorize)
df["Dimensions"] = df["Element Name"].apply(extract_dimensions)

# Initialize session state for filters
filter_keys = [
    "Color_keyword", "Color_select",
    "Element Name_keyword", "Element Name_select",
    "Category_keyword", "Category_select",
    "Dimensions_keyword", "Dimensions_select"
]

for key in filter_keys:
    if key not in st.session_state:
        st.session_state[key] = ""

# Sidebar filters
st.sidebar.header("🔍 Smart Filters")

# Clear filters button with rerun trigger
if st.sidebar.button("🔄 Clear All Filters"):
    for key in filter_keys:
        st.session_state[key] = ""
    st.rerun()

# Hybrid filter function
def hybrid_filter(df, column, label):
    keyword = st.sidebar.text_input(f"{label} contains...", value=st.session_state[f"{column}_keyword"], key=f"{column}_keyword")
    options = [v for v in df[column].dropna().unique() if keyword.lower() in str(v).lower()]
    selected = st.sidebar.selectbox(f"Pick exact {label} (optional)", [""] + sorted(options), index=0, key=f"{column}_select")

    if selected:
        return df[df[column] == selected]
    elif keyword:
        return df[df[column].str.lower().str.contains(keyword.lower(), na=False)]
    else:
        return df

# Apply filters
filtered_df = df.copy()
filtered_df = hybrid_filter(filtered_df, "Color", "Color")
filtered_df = hybrid_filter(filtered_df, "Element Name", "Element Name")
filtered_df = hybrid_filter(filtered_df, "Category", "Category")
filtered_df = hybrid_filter(filtered_df, "Dimensions", "Dimensions")

# Display results
st.title("🧱 UCS Falcon Inventory Lookup")
st.caption("Type keywords or pick exact matches. Tap 'Clear All Filters' to reset.")

# Show as table
for idx, row in filtered_df.iterrows():
    cols = st.columns([1, 1.2, 1.2, 1.2, 2.5, 1.2, 1.2])
    img_path = f"images/{row['DesignID']}_{row['ElementID']}.png"
    if os.path.exists(img_path):
        cols[0].image(img_path, width=60)
    else:
        cols[0].write("❌")

    cols[1].markdown(f"**{row['DesignID']}**")
    cols[2].markdown(f"`{row['ElementID']}`")
    cols[3].markdown(f"`{row['Color']}`")
    cols[4].markdown(f"{row['Element Name']}")
    cols[5].markdown(f"`{row['Category']}`")
    cols[6].markdown(f"`{row['Dimensions']}`")

