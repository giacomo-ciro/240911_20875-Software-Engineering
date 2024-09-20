import streamlit as st

def read_content(content):
    """Reads the pasted content and returns it as a list of lines."""
    return content.replace(' ', '').splitlines()

def compare_contents(content1, content2):
    """Compares two lists of lines and returns True if they are the same."""
    return content1 == content2

# Streamlit App
st.title('Truth Table Comparison Tool')

# Text area for the first truth table
content1 = st.text_area("Paste the first truth table content here")

# Text area for the second truth table
content2 = st.text_area("Paste the second truth table content here")

if content1 and content2:
    # Read the content of both tables
    content1_lines = read_content(content1)
    content2_lines = read_content(content2)
    
    # Compare the contents
    if compare_contents(content1_lines, content2_lines):
        st.success("The two truth table contents are identical!")
    else:
        st.error("The two truth table contents are different!")
        
    # Option to show the contents of both inputs
    
    with st.expander("Show table contents"):
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Table 1 Content:")
            st.text("\n".join(content1_lines))
        with col2:
            st.subheader("Table 2 Content:")
            st.text("\n".join(content2_lines))