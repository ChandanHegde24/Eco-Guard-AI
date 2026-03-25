# 🌍 Eco-Guard-AI

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-success?style=flat-square)](https://github.com/ChandanHegde24/Eco-Guard-AI)

**Intelligent Environmental Monitoring & Protection System**

_Leveraging AI to protect our planet, one insight at a time._

</div>

---

## 🎯 Vision

Eco-Guard-AI is an advanced environmental monitoring and protection platform that harnesses the power of Artificial Intelligence to detect, analyze, and mitigate environmental threats in real-time. Our mission is to empower communities and organizations with data-driven insights to build a sustainable future.

---

## ✨ Key Features

- **🤖 AI-Powered Detection**: Machine learning models for environmental anomaly detection
- **📊 Real-Time Monitoring**: Live data streams from multiple environmental sensors
- **🌱 Predictive Analytics**: Forecast environmental trends before they become critical
- **📱 User-Friendly Dashboard**: Intuitive interface for tracking ecological metrics
- **🔔 Smart Alerts**: Intelligent notification system for environmental risks
- **📈 Data Visualization**: Comprehensive charts and graphs for trend analysis
- **🌐 Scalable Architecture**: Built to handle massive amounts of environmental data

---

## 🏗️ Project Structure

```
Eco-Guard-AI/
├── frontend/
│   └── dashboard.py       # Streamlit-based dashboard UI
├── backend/
│   ├── main.py            # FastAPI application entry point
│   ├── core/
│   │   ├── config.py      # Project settings & Earth Engine config
│   │   └── risk_scoring.py# Climate risk assessment & alerts
│   └── data_layer/
│       ├── gee_client.py  # Google Earth Engine satellite data fetcher
│       └── ai_layer/
│           ├── vegetation_index.py  # NDVI/NDWI change detection
│           └── siamese_cnn.py       # Siamese CNN model (placeholder)
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Google Earth Engine account (for satellite data access)
- Git

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/ChandanHegde24/Eco-Guard-AI.git
   cd Eco-Guard-AI
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create Environment File**
   ```bash
   cp .env.example .env
   ```

4. **Authenticate Google Earth Engine**
   ```bash
   earthengine authenticate
   ```

5. **Set your Earth Engine Project ID**
   Set the environment variable or edit `backend/core/config.py`:
   ```bash
   export EE_PROJECT_ID="your-google-cloud-project-id"
   ```

6. **Start the Backend (FastAPI)**
   ```bash
   cd backend
   python main.py
   ```

7. **Start the Frontend (Streamlit Dashboard)**
   In a separate terminal:
   ```bash
   streamlit run frontend/dashboard.py
   ```

8. **Access the Application**
   ```
   Backend API:  http://localhost:8000
   Dashboard:    http://localhost:8501
   ```

9. **Run Tests**
   ```bash
   pytest backend/tests -q
   ```

---

## ✅ Operational Endpoints

- `GET /health` - liveness endpoint for service availability
- `GET /ready` - readiness endpoint with database and Earth Engine checks
- `GET /api/v1/analysis/recent` - recent analysis history for the dashboard

---

## 🔁 Continuous Integration

The project now includes a GitHub Actions workflow at `.github/workflows/ci.yml` that runs on push and pull request:

- Install dependencies
- Run backend tests with `pytest`

---

## 📊 How It Works

```
Sensor Data → Data Pipeline → AI Models → Analysis → Alerts & Dashboard
```

1. **Data Collection**: Environmental sensors feed real-time data
2. **Processing**: Data is normalized and prepared for ML models
3. **Analysis**: AI algorithms identify patterns and anomalies
4. **Insights**: Results are visualized and actionable alerts are generated
5. **Action**: Users receive recommendations for environmental protection

---

## 🔧 Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Python, FastAPI, Uvicorn |
| **Frontend** | Streamlit, Folium |
| **ML/AI** | PyTorch (Siamese CNN) |
| **Satellite Data** | Google Earth Engine (Sentinel-2) |
| **APIs** | RESTful APIs |

---

## 📈 Use Cases

- 🌊 **Water Quality Monitoring**: Track pollution levels in water bodies
- 🌬️ **Air Quality Assessment**: Real-time air pollution detection and forecasting
- 🌳 **Forest Management**: Wildfire detection and prevention
- 🌡️ **Climate Tracking**: Temperature and weather anomaly detection
- 🏭 **Industrial Emissions**: Monitor and control factory emissions
- 🐾 **Wildlife Protection**: Ecosystem health monitoring

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for more details.

---

## 📚 Documentation

- [Installation Guide](docs/INSTALLATION.md)
- [API Reference](docs/API.md)
- [User Guide](docs/USER_GUIDE.md)
- [Developer Guide](docs/DEVELOPER.md)

---

## 🐛 Known Issues

Currently tracking issues on our [GitHub Issues Page](https://github.com/ChandanHegde24/Eco-Guard-AI/issues). Feel free to report bugs or suggest features!

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

**Developer**: [Chandan Hegde](https://github.com/ChandanHegde24)

---

## 📞 Get in Touch

- 💬 **GitHub Issues**: [Report a bug](https://github.com/ChandanHegde24/Eco-Guard-AI/issues)
- 🌐 **GitHub Discussions**: [Start a discussion](https://github.com/ChandanHegde24/Eco-Guard-AI/discussions)
- ✉️ **Email**: Reach out for collaboration opportunities

---

## 🌟 Support

If you find Eco-Guard-AI helpful, please consider:
- ⭐ Starring the repository
- 🔗 Sharing with your network
- 💡 Contributing ideas and improvements
- 🐛 Reporting bugs and suggesting features

---

<div align="center">

**Making the world a greener place, one algorithm at a time** 🌱

_Last Updated: March 11, 2026_

</div>