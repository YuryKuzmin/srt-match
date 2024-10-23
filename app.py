import streamlit as st
import csv
import io

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

def split_translation_into_segments(translation_text, num_segments):
    """Split the translation text into roughly equal segments based on punctuation."""
    sentences = []
    current_sentence = []
    
    for word in translation_text.replace('\n', ' ').split():
        current_sentence.append(word)
        if word.endswith(('.', '!', '?', '。', '！', '？')):
            sentences.append(' '.join(current_sentence))
            current_sentence = []
    
    if current_sentence:
        sentences.append(' '.join(current_sentence))
    
    segments = [[] for _ in range(num_segments)]
    current_segment = 0
    
    for sentence in sentences:
        segments[current_segment].append(sentence)
        current_segment = (current_segment + 1) % num_segments
    
    return [' '.join(segment) for segment in segments]

def create_translated_srt_and_csv(english_srt, translation_text):
    """Create both SRT and CSV files using English timestamps and translated text."""
    blocks = parse_srt_timestamps(english_srt)
    translated_segments = split_translation_into_segments(translation_text, len(blocks))
    
    # Generate SRT content
    srt_lines = []
    # Generate CSV data
    csv_data = []
    csv_headers = ['speaker', 'transcription', 'translation', 'start_time', 'end_time']
    
    for i, (block, translated_text) in enumerate(zip(blocks, translated_segments)):
        # SRT format
        srt_lines.extend([
            str(i + 1),
            block['time'],
            translated_text,
            ''
        ])
        
        # CSV format
        start_time, end_time = parse_time_range(block['time'])
        csv_data.append({
            'speaker': 'Speaker 1',
            'transcription': translated_text,
            'translation': translated_text,
            'start_time': f"{start_time:.3f}",
            'end_time': f"{end_time:.3f}"
        })
    
    # Create CSV content
    csv_output = io.StringIO()
    writer = csv.DictWriter(csv_output, fieldnames=csv_headers)
    writer.writeheader()
    writer.writerows(csv_data)
    
    return '\n'.join(srt_lines), csv_output.getvalue()

# Streamlit interface
st.title('SRT and CSV Translation Helper')
st.write('This tool helps you create both translated SRT and CSV files using timestamps from an English SRT file.')

# File upload for English SRT
english_srt_file = st.file_uploader("Upload English SRT file", type=['srt', 'txt'])

# Text area for translated text
translation_text = st.text_area("Paste your translated text here", height=200)

if st.button('Generate Files'):
    if english_srt_file is not None and translation_text:
        try:
            # Read the English SRT file
            english_srt_content = english_srt_file.getvalue().decode('utf-8')
            
            # Generate both SRT and CSV content
            translated_srt, csv_content = create_translated_srt_and_csv(english_srt_content, translation_text)
            
            # Create two columns for the output
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Generated SRT")
                st.text_area("SRT Content", translated_srt, height=300)
                st.download_button(
                    label="Download SRT file",
                    data=translated_srt.encode('utf-8'),
                    file_name="translated.srt",
                    mime="text/plain"
                )
            
            with col2:
                st.subheader("Generated CSV")
                st.text_area("CSV Content", csv_content, height=300)
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
1. Upload your English SRT file
2. Paste your translated text
3. Click 'Generate Files'
4. Download both the SRT and CSV files

Note: 
- The tool will try to match the translated text to the original timing
- The CSV file follows the specified format with Speaker 1 as the default speaker
- Both transcription and translation columns in the CSV contain the same translated text
- Times are converted to seconds for the CSV format
""")
