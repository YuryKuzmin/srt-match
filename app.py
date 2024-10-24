import streamlit as st
import csv
import io
import re

def split_into_sentences(text):
    """Split text into sentences using punctuation marks."""
    # Split on multiple punctuation marks while preserving them
    sentences = re.split(r'([.!?。！？])', text)
    # Combine sentences with their punctuation marks and filter empty strings
    complete_sentences = []
    current_sentence = ''
    
    for i in range(0, len(sentences), 2):
        current_sentence = sentences[i]
        if i + 1 < len(sentences):  # If there's punctuation
            current_sentence += sentences[i + 1]
        if current_sentence.strip():
            complete_sentences.append(current_sentence.strip())
    
    return complete_sentences

def create_csv_with_timing(translation_text, cps):
    """Create CSV file with timing based on character count and specified CPS."""
    sentences = split_into_sentences(translation_text)
    
    csv_data = []
    csv_headers = ['speaker', 'transcription', 'translation', 'start_time', 'end_time']
    current_time = 0.0
    
    # Create CSV entries
    for sentence in sentences:
        # Calculate duration based on character count and CPS
        duration = len(sentence) / cps
        end_time = current_time + duration
        
        csv_data.append({
            'speaker': 'Speaker 1',
            'transcription': sentence,
            'translation': sentence,
            'start_time': f"{current_time:.3f}",
            'end_time': f"{end_time:.3f}"
        })
        
        current_time = end_time
    
    # Create CSV content
    csv_output = io.StringIO()
    writer = csv.DictWriter(csv_output, fieldnames=csv_headers)
    writer.writeheader()
    writer.writerows(csv_data)
    
    return csv_output.getvalue()

# Streamlit interface
st.title('Subtitle CSV Generator')
st.write('This tool creates a CSV file with timing based on character count and customizable reading speed.')

# CPS input with default value
cps = st.number_input(
    "Characters per second (CPS)",
    min_value=1.0,
    max_value=30.0,
    value=15.26,
    step=0.1,
    help="Number of characters that can be read per second. Default is 15.26"
)

# Text area for translated text
translation_text = st.text_area("Paste your translated text here", height=200)

if st.button('Generate CSV'):
    if translation_text:
        try:
            # Generate CSV content
            csv_content = create_csv_with_timing(translation_text, cps)
            
            # Display preview
            st.subheader("Generated CSV Preview")
            st.text_area("CSV Content", csv_content, height=300)
            
            # Download button
            st.download_button(
                label="Download CSV file",
                data=csv_content.encode('utf-8'),
                file_name="translated.csv",
                mime="text/csv"
            )
            
            # Display total duration
            sentences = split_into_sentences(translation_text)
            total_chars = sum(len(sentence) for sentence in sentences)
            total_duration = total_chars / cps
            st.info(f"""
            Statistics:
            - Total characters: {total_chars}
            - Total duration: {total_duration:.2f} seconds ({int(total_duration/60)}:{int(total_duration%60):02d})
            - Average characters per sentence: {total_chars/len(sentences):.1f}
            """)
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please provide the translated text.")

st.markdown("""
### How to use:
1. Adjust the Characters per Second (CPS) if needed (default: 15.26)
2. Paste your translated text
3. Click 'Generate CSV'
4. Download the generated CSV file

Note: 
- The tool automatically splits text into sentences using punctuation
- Timing is calculated based on character count and CPS
- Each sentence gets its own line in the CSV
- The CSV includes speaker, transcription, translation, and timing information
""")
