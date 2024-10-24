import streamlit as st
import csv
import io
import re

def parse_srt_timestamps(srt_content):
    """Parse SRT file and extract timestamp blocks with their text."""
    blocks = []
    current_block = {'index': '', 'time': '', 'text': []}
    
    for line in srt_content.strip().split('\n'):
        line = line.strip()
        if not line:
            if current_block['text']:
                blocks.append(current_block.copy())
                current_block = {'index': '', 'time': '', 'text': []}
        elif current_block['index'] == '':
            current_block['index'] = line
        elif current_block['time'] == '':
            current_block['time'] = line
        else:
            current_block['text'].append(line)
    
    if current_block['text']:
        blocks.append(current_block)
    
    return blocks

def convert_timestamp_to_seconds(timestamp):
    """Convert SRT timestamp to seconds."""
    hours, minutes, seconds = timestamp.replace(',', '.').split(':')
    return float(hours) * 3600 + float(minutes) * 60 + float(seconds)

def parse_time_range(time_range):
    """Parse SRT time range and return start and end times in seconds."""
    start, end = time_range.split(' --> ')
    return convert_timestamp_to_seconds(start), convert_timestamp_to_seconds(end)

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

def allocate_time_for_sentences(sentences, total_duration):
    """Allocate time for each sentence based on character count with 15.26 chars/second."""
    CHARS_PER_SECOND = 15.26
    
    # Calculate total characters
    total_chars = sum(len(sentence) for sentence in sentences)
    
    # Calculate ideal duration for each sentence
    ideal_durations = [len(sentence) / CHARS_PER_SECOND for sentence in sentences]
    ideal_total = sum(ideal_durations)
    
    # Scale durations to match total available duration
    scale_factor = total_duration / ideal_total
    scaled_durations = [duration * scale_factor for duration in ideal_durations]
    
    return scaled_durations

def create_csv_with_intelligent_timing(english_srt, translation_text):
    """Create CSV file with intelligent timing based on character count."""
    blocks = parse_srt_timestamps(english_srt)
    sentences = split_into_sentences(translation_text)
    
    csv_data = []
    csv_headers = ['speaker', 'transcription', 'translation', 'start_time', 'end_time']
    current_time = 0.0
    
    # Get total duration from original SRT
    total_duration = sum(
        parse_time_range(block['time'])[1] - parse_time_range(block['time'])[0]
        for block in blocks
    )
    
    # Allocate durations based on character count
    durations = allocate_time_for_sentences(sentences, total_duration)
    
    # Create CSV entries
    for sentence, duration in zip(sentences, durations):
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
st.write('This tool creates a CSV file with intelligent timing based on character count (15.26 characters per second).')

# File upload for English SRT
english_srt_file = st.file_uploader("Upload English SRT file (for timing reference)", type=['srt', 'txt'])

# Text area for translated text
translation_text = st.text_area("Paste your translated text here", height=200)

if st.button('Generate CSV'):
    if english_srt_file is not None and translation_text:
        try:
            # Read the English SRT file
            english_srt_content = english_srt_file.getvalue().decode('utf-8')
            
            # Generate CSV content
            csv_content = create_csv_with_intelligent_timing(english_srt_content, translation_text)
            
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
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please upload an English SRT file and provide the translated text.")

st.markdown("""
### How to use:
1. Upload your English SRT file (used only for total duration reference)
2. Paste your translated text
3. Click 'Generate CSV'
4. Download the generated CSV file

Note: 
- The tool intelligently allocates time for each subtitle based on character count
- Uses standard reading speed of 15.26 characters per second
- Preserves total video duration from original SRT
- Splits text into natural sentences using punctuation
- CSV includes speaker, transcription, translation, and timing information
""")
