"""
Streamlit GUI for Bill Management Agent
Beautiful web interface using VLM for bill processing
"""

import streamlit as st
import plotly.express as px
import pandas as pd
import json
from pathlib import Path
import sys

# Add parent directory to path
#sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
print("Path=", str(Path(__file__).parent.parent.parent))

from bill_processor import BillProcessor
from src.utils.vlm_provider import ModelManager
from src.database.db_manager import DatabaseManager
from src.config.model_config import MODEL_PROVIDERS, DEFAULT_VISION_MODEL
from src.utils.json_formatter import create_csv_export


# Page config
st.set_page_config(
    page_title="💰 Bill Management Agent",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .tech-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        margin: 0.25rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 0.5rem;
        font-size: 0.8rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'processed_result' not in st.session_state:
    st.session_state.processed_result = None
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = DatabaseManager()


def initialize_system():
    """Initialize VLM model manager and processor"""
    model_manager = ModelManager(
        primary_model=st.session_state.get('selected_model', DEFAULT_VISION_MODEL),
        fallback_model=st.session_state.get('fallback_model', 'groq_llama_scout')
    )
    
    processor = BillProcessor(
        model_manager=model_manager,
        db_manager=st.session_state.db_manager
    )
    
    return processor


def render_sidebar():
    """Render sidebar with VLM model selection"""
    st.sidebar.title("⚙️ Settings")
    
    st.sidebar.markdown("### 🤖 Vision Language Model")
    
    # Model selection
    model_options = list(MODEL_PROVIDERS.keys())
    model_labels = [
        f"{MODEL_PROVIDERS[key]['model'].split('/')[-1]}"
        for key in model_options
    ]
    
    selected_idx = st.sidebar.selectbox(
        "Primary VLM",
        range(len(model_options)),
        format_func=lambda x: model_labels[x],
        index=0
    )
    
    st.session_state.selected_model = model_options[selected_idx]
    
    # Show model info
    config = MODEL_PROVIDERS[st.session_state.selected_model]
    st.sidebar.info(f"""
**VLM Details:**
- Provider: {config['provider']}
- Model: {config['model'].split('/')[-1]}
- Speed: {config['speed']}
- Cost: FREE ✅
    """)
    
    # Fallback
    use_fallback = st.sidebar.checkbox("Enable automatic fallback", value=True)
    st.session_state.fallback_model = 'groq_llama_scout' if use_fallback else None
    
    st.sidebar.divider()
    
    # Statistics
    st.sidebar.markdown("### 📊 Statistics")
    stats = st.session_state.db_manager.get_statistics()
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("Bills", stats['total_bills'])
    with col2:
        st.metric("Total", f"${stats['total_spent']:.0f}")
    
    st.sidebar.metric("Avg/Bill", f"${stats['average_bill']:.2f}")


def render_upload_section():
    """Render file upload section"""
    st.header("📤 Upload Bill Image")
    st.markdown("Upload a clear image of your bill or receipt. The VLM will analyze it directly!")
    
    uploaded_file = st.file_uploader(
        "Choose file (JPG, PNG, or PDF)",
        type=['jpg', 'jpeg', 'png', 'pdf']
    )
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        process_button = st.button("🔄 Process Bill", type="primary", use_container_width=True)
    
    with col2:
        if uploaded_file:
            st.success(f"✅ {uploaded_file.name}")
    
    return uploaded_file, process_button


def process_bill_file(uploaded_file):
    """Process uploaded bill using VLM"""
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    
    file_path = upload_dir / uploaded_file.name
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    with st.spinner("🔍 Analyzing with Vision Language Model..."):
        processor = initialize_system()
        result = processor.process_bill(str(file_path))
    
    return result


def render_results(result):
    """Render VLM processing results"""
    if not result['success']:
        st.error(f"❌ {result['error']}")
        if 'details' in result:
            with st.expander("Details"):
                st.json(result['details'])
        return
    
    data = result['data']
    
    st.success("✅ Bill processed successfully with VLM!")
    
    # Bill Info
    st.header("🏪 Bill Information")
    meta = data['bill_metadata']
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Merchant", meta['merchant_name'])
    with col2:
        st.metric("Date", meta['bill_date'])
    with col3:
        quality_stars = {"excellent": "⭐⭐⭐⭐⭐", "good": "⭐⭐⭐⭐", "fair": "⭐⭐⭐", "poor": "⭐"}.get(meta['image_quality'], "⭐⭐⭐")
        st.metric("Quality", f"{quality_stars}")
    with col4:
        st.metric("Confidence", f"{meta['overall_confidence']:.0%}")
    
    # VLM model used
    if meta.get('fallback_used'):
        st.warning(f"🔄 Used fallback model: {meta['model_used']}")
    else:
        st.info(f"🤖 Analyzed by: {meta['model_used']}")
    
    st.divider()
    
    # Summary
    st.header("💳 Summary")
    summary = data['summary']
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total", f"${summary['total_amount']:.2f}")
    with col2:
        st.metric("Items", summary['item_count'])
    with col3:
        st.metric("Top Category", summary['highest_spending_category'].title())
    with col4:
        avg_conf = data['quality_metrics'].get('average_confidence', 0.0)
        st.metric("Confidence", f"{avg_conf:.0%}")
    
    st.divider()
    
    # Category Breakdown
    st.header("📈 Category Breakdown")
    
    breakdown = summary['category_breakdown']
    categories = [k for k, v in breakdown.items() if v > 0]
    amounts = [v for k, v in breakdown.items() if v > 0]
    
    if categories:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = px.bar(
                x=categories,
                y=amounts,
                labels={'x': 'Category', 'y': 'Amount ($)'},
                title='Spending by Category',
                color=amounts,
                color_continuous_scale='blues'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig_pie = px.pie(
                values=amounts,
                names=categories,
                title='Distribution',
                hole=0.4
            )
            st.plotly_chart(fig_pie, use_container_width=True)
    
    st.divider()
    
    # Expenses
    st.header("📝 Expense Items")
    
    if data['expenses']:
        df = pd.DataFrame(data['expenses'])
        df['amount'] = df['amount'].apply(lambda x: f"${x:.2f}")
        df['confidence'] = df['confidence'].apply(lambda x: f"{x:.0%}")
        df['category'] = df['category'].str.title()
        
        st.dataframe(
            df.rename(columns={
                'description': 'Description',
                'amount': 'Amount',
                'category': 'Category',
                'confidence': 'Confidence'
            }),
            use_container_width=True,
            hide_index=True
        )
    
    st.divider()
    
    # Insights
    st.header("💡 Insights")
    insights = data['insights']
    
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**Key Insight:** {insights.get('primary_insight', 'N/A')}")
    with col2:
        st.success(f"**Quality:** {insights.get('quality_notes', 'Good')}")
    
    # Downloads
    st.divider()
    st.header("📥 Export")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        json_str = json.dumps(data, indent=2)
        st.download_button(
            "📄 JSON",
            json_str,
            f"bill_{result['bill_id']}.json",
            "application/json",
            use_container_width=True
        )
    
    with col2:
        csv_str = create_csv_export(data['expenses'])
        st.download_button(
            "📊 CSV",
            csv_str,
            f"expenses_{result['bill_id']}.csv",
            "text/csv",
            use_container_width=True
        )
    
    with col3:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.processed_result = None
            st.rerun()
    
    with st.expander("🔍 Raw JSON"):
        st.json(data)


def main():
    """Main application"""
    # Header
    st.markdown('<div class="main-header">💰 Bill Management Agent</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center; margin-bottom: 2rem;'>
        <span class='tech-badge'>Vision Language Models</span>
        <span class='tech-badge'>Multi-Provider</span>
        <span class='tech-badge'>Auto-Fallback</span>
        <span class='tech-badge'>FREE</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    render_sidebar()
    
    # Main content
    uploaded_file, process_button = render_upload_section()
    
    # Process
    if process_button and uploaded_file:
        result = process_bill_file(uploaded_file)
        st.session_state.processed_result = result
    
    # Results
    if st.session_state.processed_result:
        st.divider()
        render_results(st.session_state.processed_result)
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>Powered by Vision Language Models 🤖</p>
        <p style='font-size: 0.8rem;'>OpenRouter Gemini (Primary) + Groq Llama (Fallback)</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()