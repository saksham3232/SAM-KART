# ============================================================================
# INTERACTIVE DATA DASHBOARD - STREAMLIT (EXCEL SUPPORT + FIXED WIDTH)
# A comprehensive data exploration and visualization tool
# ============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Interactive Data Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'df' not in st.session_state:
    st.session_state.df = None
if 'filter_values' not in st.session_state:
    st.session_state.filter_values = {}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def detect_numeric_columns(df):
    """Identify numeric columns for analysis"""
    return df.select_dtypes(include=[np.number]).columns.tolist()

def detect_categorical_columns(df):
    """Identify categorical columns for filtering"""
    return df.select_dtypes(include=['object']).columns.tolist()

def calculate_summary_statistics(df, numeric_cols):
    """Calculate summary statistics for numeric columns"""
    stats = {
        'Column': [],
        'Count': [],
        'Mean': [],
        'Median': [],
        'Std Dev': [],
        'Min': [],
        'Max': []
    }
    
    for col in numeric_cols:
        stats['Column'].append(col)
        stats['Count'].append(df[col].count())
        stats['Mean'].append(f"{df[col].mean():.2f}")
        stats['Median'].append(f"{df[col].median():.2f}")
        stats['Std Dev'].append(f"{df[col].std():.2f}")
        stats['Min'].append(f"{df[col].min():.2f}")
        stats['Max'].append(f"{df[col].max():.2f}")
    
    return pd.DataFrame(stats)

def create_histogram(df, column, key_id=""):
    """Create interactive histogram"""
    fig = px.histogram(
        df, x=column, nbins=30,
        title=f'Distribution of {column}',
        labels={column: column},
        color_discrete_sequence=['#1f77b4']
    )
    fig.update_layout(xaxis_title=column, yaxis_title='Frequency', height=400)
    return fig

def create_scatter_plot(df, x_col, y_col, color_col=None, key_id=""):
    """Create interactive scatter plot"""
    fig = px.scatter(
        df, x=x_col, y=y_col, color=color_col,
        title=f'{x_col} vs {y_col}',
        height=500
    )
    fig.update_layout(hovermode='closest')
    return fig

def create_bar_chart(df, x_col, y_col, title=None, key_id=""):
    """Create interactive bar chart"""
    grouped_data = df.groupby(x_col)[y_col].sum().reset_index().sort_values(y_col, ascending=False)
    fig = px.bar(
        grouped_data, x=x_col, y=y_col,
        title=title or f'{y_col} by {x_col}',
        color=y_col,
        color_continuous_scale='Viridis'
    )
    fig.update_layout(height=400)
    return fig

def create_line_chart(df, x_col, y_col, color_col=None, key_id=""):
    """Create interactive line chart"""
    if color_col and color_col in df.columns:
        fig = px.line(
            df, x=x_col, y=y_col, color=color_col,
            title=f'{y_col} over {x_col}',
            markers=True, height=400
        )
    else:
        fig = px.line(
            df, x=x_col, y=y_col,
            title=f'{y_col} over {x_col}',
            markers=True, height=400
        )
    return fig

def create_box_plot(df, x_col, y_col, key_id=""):
    """Create interactive box plot"""
    fig = px.box(
        df, x=x_col, y=y_col,
        title=f'Box Plot: {y_col} by {x_col}',
        height=400
    )
    return fig

def create_pie_chart(df, values_col, names_col, title=None, key_id=""):
    """Create interactive pie chart"""
    grouped_data = df.groupby(names_col)[values_col].sum().reset_index()
    fig = px.pie(
        grouped_data, values=values_col, names=names_col,
        title=title or f'{values_col} Distribution by {names_col}',
        height=500
    )
    return fig

def create_correlation_heatmap(df, numeric_cols, key_id=""):
    """Create correlation heatmap"""
    corr_matrix = df[numeric_cols].corr()
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=np.round(corr_matrix.values, 2),
        texttemplate='%{text:.2f}',
        textfont={"size": 10}
    ))
    fig.update_layout(
        title='Correlation Heatmap',
        height=500,
        xaxis_title='',
        yaxis_title=''
    )
    return fig

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    # Header
    st.markdown("# 📊 Interactive Data Dashboard")
    st.markdown("---")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("**Explore, analyze, and visualize your data with interactive charts and filters.**")
    with col2:
        st.info("✨ Features: CSV/Excel Upload • Dynamic Charts • Filtering • Statistics")
    
    # Sidebar for file upload and configuration
    with st.sidebar:
        st.markdown("## 📁 Data Upload")
        
        # File uploader - NOW SUPPORTS CSV, XLSX, XLS
        uploaded_file = st.file_uploader(
            "Choose a CSV or Excel file",
            type=['csv', 'xlsx', 'xls'],
            help="Upload CSV, Excel (.xlsx) or (.xls) file to begin analysis"
        )
        
        if uploaded_file is not None:
            try:
                # Handle different file types
                file_extension = uploaded_file.name.split('.')[-1].lower()
                
                if file_extension == 'csv':
                    df = pd.read_csv(uploaded_file)
                else:  # xlsx or xls
                    df = pd.read_excel(uploaded_file)
                
                st.session_state.df = df
                st.session_state.uploaded_file = uploaded_file
                st.success(f"✅ File uploaded! ({len(df)} rows × {len(df.columns)} columns)")
                
            except Exception as e:
                st.error(f"❌ Error loading file: {str(e)}")
                st.info("💡 Supported formats: CSV, Excel (.xlsx, .xls)")
                return
        else:
            st.warning("📤 Please upload a CSV or Excel file to get started")
            st.stop()
    
    if st.session_state.df is None:
        st.stop()
    
    df = st.session_state.df
    numeric_cols = detect_numeric_columns(df)
    categorical_cols = detect_categorical_columns(df)

    # =========================================================================
    # TAB STRUCTURE
    # =========================================================================

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Overview",
        "🔍 Exploration",
        "📊 Visualizations",
        "🎯 Advanced Analysis",
        "📋 Raw Data"
    ])

    # =========================================================================
    # TAB 1: OVERVIEW
    # =========================================================================

    with tab1:
        st.markdown("## Dataset Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Total Rows", f"{len(df):,}")
        with col2:
            st.metric("📋 Total Columns", len(df.columns))
        with col3:
            st.metric("🔢 Numeric Columns", len(numeric_cols))
        with col4:
            st.metric("🏷️ Categorical Columns", len(categorical_cols))
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Column Information")
            col_info = pd.DataFrame({
                'Column': df.columns,
                'Data Type': df.dtypes.astype(str),
                'Non-Null Count': df.count(),
                'Null Count': df.isnull().sum()
            })
            st.dataframe(col_info, width='stretch', hide_index=True)
        
        with col2:
            st.markdown("### Summary Statistics")
            if numeric_cols:
                summary_df = calculate_summary_statistics(df, numeric_cols)
                st.dataframe(summary_df, width='stretch', hide_index=True)
            else:
                st.info("No numeric columns found in the dataset")
        
        st.markdown("### Missing Values Analysis")
        missing_data = pd.DataFrame({
            'Column': df.columns,
            'Missing Count': df.isnull().sum(),
            'Missing %': (df.isnull().sum() / len(df) * 100).round(2)
        })
        missing_data = missing_data[missing_data['Missing Count'] > 0].sort_values('Missing %', ascending=False)
        
        if len(missing_data) > 0:
            fig_missing = px.bar(
                missing_data, x='Column', y='Missing %',
                title='Missing Values by Column',
                color='Missing %',
                color_continuous_scale='Reds',
                height=400
            )
            st.plotly_chart(fig_missing, key="missing_values_chart")
        else:
            st.success("✅ No missing values found!")

    # =========================================================================
    # TAB 2: EXPLORATION
    # =========================================================================

    with tab2:
        st.markdown("## Data Exploration & Filtering")
        st.markdown("### 🎯 Apply Filters")
        
        filter_cols = st.columns(min(len(categorical_cols), 4) if categorical_cols else 1)
        filtered_df = df.copy()
        
        for idx, col in enumerate(categorical_cols):
            with filter_cols[idx % len(filter_cols)]:
                selected_values = st.multiselect(
                    f"Select {col}",
                    options=df[col].unique(),
                    default=df[col].unique(),
                    key=f"filter_{col}"
                )
                if selected_values:
                    filtered_df = filtered_df[filtered_df[col].isin(selected_values)]
        
        # Row range filter
        st.markdown("### 🔢 Limit number of datapoints")
        min_idx, max_idx = 0, len(filtered_df) - 1
        if max_idx > 0:
            start_idx, end_idx = st.slider(
                "Select row range to analyze",
                min_value=min_idx,
                max_value=max_idx,
                value=(min_idx, min(max_idx, 500)),
                key="exploration_row_range"
            )
            filtered_df = filtered_df.iloc[start_idx:end_idx + 1]
        
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Filtered Rows", f"{len(filtered_df):,}")
        with col2:
            st.metric("📉 Rows Removed", f"{len(df) - len(filtered_df):,}")
        with col3:
            percentage = (len(filtered_df) / len(df) * 100) if len(df) > 0 else 0
            st.metric("📈 Data Retained", f"{percentage:.1f}%")
        
        st.markdown("---")
        if numeric_cols:
            st.markdown("### 📊 Statistics for Filtered Data")
            numeric_col = st.selectbox("Select a numeric column to analyze:", numeric_cols, key="exploration_numeric")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("Mean", f"{filtered_df[numeric_col].mean():.2f}")
            with col2:
                st.metric("Median", f"{filtered_df[numeric_col].median():.2f}")
            with col3:
                st.metric("Std Dev", f"{filtered_df[numeric_col].std():.2f}")
            with col4:
                st.metric("Min", f"{filtered_df[numeric_col].min():.2f}")
            with col5:
                st.metric("Max", f"{filtered_df[numeric_col].max():.2f}")
            
            fig = create_histogram(filtered_df, numeric_col, "exploration")
            st.plotly_chart(fig, key="exploration_histogram")

    # =========================================================================
    # TAB 3: VISUALIZATIONS
    # =========================================================================

    with tab3:
        st.markdown("## Interactive Visualizations")
        st.markdown("### 🎯 Visualization Filters")
        
        filter_cols = st.columns(min(len(categorical_cols), 4) if categorical_cols else 1)
        filtered_df_viz = df.copy()
        
        for idx, col in enumerate(categorical_cols):
            with filter_cols[idx % len(filter_cols)]:
                selected_values = st.multiselect(
                    f"Select {col} (Viz)",
                    options=df[col].unique(),
                    default=df[col].unique(),
                    key=f"viz_filter_{col}"
                )
                if selected_values:
                    filtered_df_viz = filtered_df_viz[filtered_df_viz[col].isin(selected_values)]
        
        # Row range for visualization
        st.markdown("### 🔢 Limit number of datapoints for charts")
        min_idx, max_idx = 0, len(filtered_df_viz) - 1
        if max_idx > 0:
            v_start, v_end = st.slider(
                "Select row range for charts",
                min_value=min_idx,
                max_value=max_idx,
                value=(min_idx, min(max_idx, 1000)),
                key="viz_row_range"
            )
            filtered_df_viz = filtered_df_viz.iloc[v_start:v_end + 1]
        
        st.markdown("---")
        chart_type = st.selectbox(
            "Select chart type:",
            ["Histogram", "Scatter Plot", "Bar Chart", "Line Chart", "Box Plot", "Pie Chart"]
        )
        
        col1, col2 = st.columns(2)
        
        if chart_type == "Histogram":
            with col1:
                x_col = st.selectbox("Select column:", numeric_cols, key="hist_col")
            fig = create_histogram(filtered_df_viz, x_col, "viz_hist")
            st.plotly_chart(fig, key="viz_histogram")
            
        elif chart_type == "Scatter Plot":
            with col1:
                x_col = st.selectbox("X-axis:", numeric_cols, key="scatter_x")
            with col2:
                y_col = st.selectbox(
                    "Y-axis:", numeric_cols,
                    key="scatter_y",
                    index=1 if len(numeric_cols) > 1 else 0
                )
            color_col = None
            if categorical_cols:
                color_col = st.selectbox(
                    "Color by (optional):",
                    [None] + categorical_cols,
                    key="scatter_color"
                )
            fig = create_scatter_plot(filtered_df_viz, x_col, y_col, color_col, "viz_scatter")
            st.plotly_chart(fig, key="viz_scatter")
            
        elif chart_type == "Bar Chart":
            with col1:
                x_col = st.selectbox(
                    "Category (X-axis):",
                    categorical_cols if categorical_cols else numeric_cols,
                    key="bar_x"
                )
            with col2:
                y_col = st.selectbox("Value (Y-axis):", numeric_cols, key="bar_y")
            fig = create_bar_chart(filtered_df_viz, x_col, y_col, key_id="viz_bar")
            st.plotly_chart(fig, key="viz_bar")
            
        elif chart_type == "Line Chart":
            with col1:
                x_col = st.selectbox("X-axis:", df.columns, key="line_x")
            with col2:
                y_col = st.selectbox("Y-axis:", numeric_cols, key="line_y")
            color_col = None
            if categorical_cols:
                color_col = st.selectbox(
                    "Color by (optional):",
                    [None] + categorical_cols,
                    key="line_color"
                )
            fig = create_line_chart(filtered_df_viz, x_col, y_col, color_col, "viz_line")
            st.plotly_chart(fig, key="viz_line")
            
        elif chart_type == "Box Plot":
            with col1:
                x_col = st.selectbox(
                    "Category (X-axis):",
                    categorical_cols if categorical_cols else numeric_cols,
                    key="box_x"
                )
            with col2:
                y_col = st.selectbox("Value (Y-axis):", numeric_cols, key="box_y")
            fig = create_box_plot(filtered_df_viz, x_col, y_col, "viz_box")
            st.plotly_chart(fig, key="viz_box")
            
        elif chart_type == "Pie Chart":
            with col1:
                names_col = st.selectbox(
                    "Category:",
                    categorical_cols if categorical_cols else numeric_cols,
                    key="pie_names"
                )
            with col2:
                values_col = st.selectbox("Values:", numeric_cols, key="pie_values")
            fig = create_pie_chart(filtered_df_viz, values_col, names_col, key_id="viz_pie")
            st.plotly_chart(fig, key="viz_pie")

    # =========================================================================
    # TAB 4: ADVANCED ANALYSIS
    # =========================================================================

    with tab4:
        st.markdown("## Advanced Analytics")
        
        # Row range for advanced analysis
        st.markdown("### 🔢 Limit datapoints for analysis")
        analysis_df = df.copy()
        min_idx, max_idx = 0, len(analysis_df) - 1
        if max_idx > 0:
            a_start, a_end = st.slider(
                "Select row range for advanced analysis",
                min_value=min_idx,
                max_value=max_idx,
                value=(min_idx, min(max_idx, 2000)),
                key="analysis_row_range"
            )
            analysis_df = analysis_df.iloc[a_start:a_end + 1]
        
        analysis_type = st.selectbox(
            "Select analysis type:",
            ["Correlation Analysis", "Distribution Analysis", "Comparative Analysis"]
        )
        
        st.markdown("---")
        
        if analysis_type == "Correlation Analysis":
            if len(numeric_cols) >= 2:
                st.markdown("### 📈 Correlation Matrix")
                fig = create_correlation_heatmap(analysis_df, numeric_cols, "analysis_corr")
                st.plotly_chart(fig, key="corr_heatmap")
                
                st.markdown("### 💡 Key Insights")
                corr_matrix = analysis_df[numeric_cols].corr()
                corr_pairs = []
                for i in range(len(corr_matrix.columns)):
                    for j in range(i + 1, len(corr_matrix.columns)):
                        corr_pairs.append({
                            'Pair': f"{corr_matrix.columns[i]} - {corr_matrix.columns[j]}",
                            'Correlation': corr_matrix.iloc[i, j]
                        })
                
                corr_pairs_df = pd.DataFrame(corr_pairs).sort_values(
                    'Correlation', key=abs, ascending=False
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Strongest Positive Correlations:**")
                    positive_corr = corr_pairs_df[corr_pairs_df['Correlation'] > 0].head(5)
                    st.dataframe(positive_corr, hide_index=True, width='stretch')
                with col2:
                    st.markdown("**Strongest Negative Correlations:**")
                    negative_corr = corr_pairs_df[corr_pairs_df['Correlation'] < 0].head(5)
                    st.dataframe(negative_corr, hide_index=True, width='stretch')
            else:
                st.info("⚠️ Need at least 2 numeric columns for correlation analysis")
                
        elif analysis_type == "Distribution Analysis":
            st.markdown("### 📊 Distribution Analysis")
            col1, col2 = st.columns(2)
            with col1:
                selected_cols = st.multiselect(
                    "Select columns to analyze:",
                    numeric_cols,
                    default=numeric_cols[:3] if numeric_cols else []
                )
            if selected_cols:
                for idx, col in enumerate(selected_cols):
                    fig = create_histogram(analysis_df, col, f"dist_{idx}")
                    st.plotly_chart(fig, key=f"dist_histogram_{idx}")
                    
        elif analysis_type == "Comparative Analysis":
            st.markdown("### 🔄 Comparative Analysis")
            col1, col2 = st.columns(2)
            with col1:
                groupby_col = st.selectbox(
                    "Group by:",
                    categorical_cols if categorical_cols else [None],
                    key="comp_groupby"
                )
            with col2:
                numeric_col = st.selectbox("Analyze:", numeric_cols, key="comp_numeric")
            
            if groupby_col and groupby_col != "None":
                comparison_data = analysis_df.groupby(groupby_col)[numeric_col].agg(
                    ['mean', 'sum', 'count', 'std']
                ).reset_index()
                
                col1, col2 = st.columns(2)
                with col1:
                    fig1 = px.bar(
                        comparison_data, x=groupby_col, y='mean',
                        title=f"Average {numeric_col} by {groupby_col}",
                        color='mean',
                        color_continuous_scale='Viridis'
                    )
                    st.plotly_chart(fig1, key="comp_mean_bar")
                with col2:
                    fig2 = px.bar(
                        comparison_data, x=groupby_col, y='sum',
                        title=f"Total {numeric_col} by {groupby_col}",
                        color='sum',
                        color_continuous_scale='Plasma'
                    )
                    st.plotly_chart(fig2, key="comp_sum_bar")
                
                st.markdown("### 📋 Detailed Comparison")
                st.dataframe(comparison_data, width='stretch')

    # =========================================================================
    # TAB 5: RAW DATA
    # =========================================================================

    with tab5:
        st.markdown("## Raw Data Explorer")
        st.markdown("### 🎯 Filter Data")
        
        filter_cols = st.columns(min(len(categorical_cols), 4) if categorical_cols else 1)
        filtered_df_raw = df.copy()
        
        for idx, col in enumerate(categorical_cols):
            with filter_cols[idx % len(filter_cols)]:
                selected_values = st.multiselect(
                    f"Select {col}",
                    options=df[col].unique(),
                    default=df[col].unique(),
                    key=f"raw_filter_{col}"
                )
                if selected_values:
                    filtered_df_raw = filtered_df_raw[filtered_df_raw[col].isin(selected_values)]
        
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            rows_to_show = st.slider(
                "Rows to display:",
                5, len(filtered_df_raw), 20,
                key="raw_slider"
            )
        with col2:
            sort_col = st.selectbox("Sort by:", filtered_df_raw.columns, key="raw_sort")
        with col3:
            sort_order = st.radio("Order:", ["Ascending", "Descending"], key="raw_order")
        
        filtered_df_display = filtered_df_raw.sort_values(
            by=sort_col, ascending=(sort_order == "Ascending")
        )
        
        st.markdown(
            f"### 📊 Showing {min(rows_to_show, len(filtered_df_display))} of {len(filtered_df_raw)} rows"
        )
        st.dataframe(filtered_df_display.head(rows_to_show), width='stretch')
        
        st.markdown("---")
        st.markdown("### 📥 Download Data")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            csv = filtered_df_raw.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name=f"data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col2:
            # FIXED Excel export using BytesIO
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                filtered_df_raw.to_excel(writer, index=False, sheet_name='Data')
            excel_data = output.getvalue()
            st.download_button(
                label="📥 Download as Excel",
                data=excel_data,
                file_name=f"data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        with col3:
            st.metric("Total Rows", len(filtered_df_raw))

if __name__ == "__main__":
    main()
