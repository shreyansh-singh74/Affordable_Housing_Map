# Affordable Housing Needs Mapper

A comprehensive application that combines a modern React frontend with a powerful Streamlit backend to analyze and visualize affordable housing needs across different areas.

## Features

- **Modern Frontend**: Beautiful React-based landing page with Tailwind CSS and shadcn/ui components
- **Interactive Backend**: Streamlit application with data visualization, maps, and affordability analysis
- **Real Data Analysis**: Uses Mumbai housing affordability dataset for real-world insights
- **Interactive Maps**: Folium-based maps showing affordability by area
- **Data Insights**: Comprehensive analytics including affordability indices, income vs rent analysis, and recommendations

## Quick Start

### Option 1: Use the startup script (Recommended)

```bash
./start_servers.sh
```

This will start both the frontend and backend servers automatically.

### Option 2: Manual startup

#### Backend (Streamlit)
```bash
cd affordable_housing_mapper
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py --server.port 8501
```

#### Frontend (React)
```bash
cd frontend/housing-needs-mapper
npm install
npm run dev
```

## Access the Application

- **Frontend**: http://localhost:8081 (or check terminal for actual port)
- **Backend**: http://localhost:8501

## How to Use

1. **Visit the Frontend**: Open http://localhost:8081 to see the landing page
2. **Click "Get Started"**: This will open the Streamlit app in a new tab
3. **Explore the Data**: Use the Streamlit interface to:
   - View interactive maps of affordability by area
   - Filter data by income groups
   - Analyze income vs rent relationships
   - Get recommendations for housing policy
   - View detailed statistics and charts

## Data

The application uses the Mumbai housing affordability dataset (`mumbai_housing_affordability.csv`) which includes:
- Neighborhood information
- Monthly rent prices (INR)
- Annual household income (INR)
- Geographic coordinates (Latitude/Longitude)

## Architecture

```
├── affordable_housing_mapper/     # Streamlit backend
│   ├── app.py                    # Main Streamlit application
│   ├── utils.py                  # Data processing utilities
│   ├── requirements.txt          # Python dependencies
│   └── data/                     # Dataset files
│       └── mumbai_housing_affordability.csv
├── frontend/                     # React frontend
│   └── housing-needs-mapper/     # React application
│       ├── src/
│       │   ├── components/       # UI components
│       │   ├── pages/           # Application pages
│       │   └── App.tsx          # Main app component
│       └── package.json         # Node dependencies
└── start_servers.sh             # Startup script
```

## Key Components

### Frontend Components
- **HeroSection**: Main landing page with call-to-action
- **CTASection**: Get Started section that redirects to Streamlit
- **ProblemSection**: Problem description
- **SolutionSection**: Solution overview
- **ImpactSection**: Impact metrics
- **Footer**: Application footer

### Backend Features
- **Data Processing**: Automatic column inference and data cleaning
- **Affordability Analysis**: Computes affordability indices and classifications
- **Interactive Maps**: Folium-based mapping with color-coded affordability
- **Statistics**: Comprehensive metrics and visualizations
- **Recommendations**: AI-generated policy recommendations

## Dependencies

### Backend
- Streamlit
- Pandas
- NumPy
- Folium
- Plotly
- GeoPandas
- KaggleHub

### Frontend
- React 18
- TypeScript
- Tailwind CSS
- shadcn/ui components
- React Router
- Lucide React icons

## Troubleshooting

1. **Port conflicts**: If ports 8501 or 5173 are in use, modify the startup commands to use different ports
2. **Python dependencies**: Ensure you're using Python 3.8+ and have installed all requirements
3. **Node dependencies**: Run `npm install` in the frontend directory if you encounter module errors
4. **Data loading**: Ensure the CSV file is present in the `affordable_housing_mapper/data/` directory

## Development

To modify the application:

1. **Frontend changes**: Edit files in `frontend/housing-needs-mapper/src/`
2. **Backend changes**: Edit files in `affordable_housing_mapper/`
3. **Data changes**: Replace or modify the CSV file in the data directory

The application will automatically reload when you make changes to the source files.