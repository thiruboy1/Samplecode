from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
from datetime import datetime, timezone, timedelta
import uuid
import asyncio
from dotenv import load_dotenv
import json
import random

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Kubernetes Cost Optimization Platform", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client.kubernetes_cost_optimizer

# LLM Integration
try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    emergent_llm_key = os.environ.get('EMERGENT_LLM_KEY')
    if not emergent_llm_key:
        print("Warning: EMERGENT_LLM_KEY not found in environment variables")
except ImportError:
    print("Warning: emergentintegrations not installed")
    LlmChat = None
    UserMessage = None

# Pydantic Models
class ClusterNode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    cpu_capacity: float
    memory_capacity: float
    cpu_usage: float
    memory_usage: float
    cost_per_hour: float
    node_type: str
    zone: str
    status: str

class ClusterInfo(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    provider: str
    region: str
    nodes: List[ClusterNode]
    total_cost: float
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CostAnalysis(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    cluster_id: str
    analysis_type: str
    recommendations: List[str]
    potential_savings: float
    confidence_score: float
    ai_insights: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class OptimizationRecommendation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    cluster_id: str
    type: str
    description: str
    impact: str
    savings_estimate: float
    implementation_complexity: str
    priority: str

class AnomalyAlert(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    cluster_id: str
    alert_type: str
    description: str
    severity: str
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved: bool = False

# AI Chat Service
class AIAnalysisService:
    def __init__(self):
        self.llm_chat = None
        if LlmChat and emergent_llm_key:
            self.llm_chat = LlmChat(
                api_key=emergent_llm_key,
                session_id="k8s-cost-optimizer",
                system_message="You are an expert Kubernetes cost optimization analyst. Provide detailed, actionable insights about cluster costs, resource utilization, and optimization opportunities. Always include specific recommendations and estimated savings."
            ).with_model("openai", "gpt-4o")
    
    async def analyze_cluster_costs(self, cluster: ClusterInfo) -> str:
        if not self.llm_chat:
            return "AI analysis unavailable - LLM integration not configured"
        
        cluster_data = {
            "name": cluster.name,
            "provider": cluster.provider,
            "total_cost": cluster.total_cost,
            "node_count": len(cluster.nodes),
            "total_cpu_capacity": sum(node.cpu_capacity for node in cluster.nodes),
            "total_memory_capacity": sum(node.memory_capacity for node in cluster.nodes),
            "avg_cpu_utilization": sum(node.cpu_usage for node in cluster.nodes) / len(cluster.nodes) if cluster.nodes else 0,
            "avg_memory_utilization": sum(node.memory_usage for node in cluster.nodes) / len(cluster.nodes) if cluster.nodes else 0
        }
        
        prompt = f"""
        Analyze this Kubernetes cluster for cost optimization opportunities:
        
        Cluster: {cluster_data['name']} ({cluster_data['provider']})
        Monthly Cost: ${cluster_data['total_cost']:.2f}
        Nodes: {cluster_data['node_count']}
        Total CPU: {cluster_data['total_cpu_capacity']} cores
        Total Memory: {cluster_data['total_memory_capacity']} GB
        Avg CPU Utilization: {cluster_data['avg_cpu_utilization']:.1f}%
        Avg Memory Utilization: {cluster_data['avg_memory_utilization']:.1f}%
        
        Provide a comprehensive cost analysis including:
        1. Current cost efficiency assessment
        2. Resource utilization insights
        3. Specific optimization recommendations
        4. Estimated potential savings
        5. Priority action items
        """
        
        try:
            user_message = UserMessage(text=prompt)
            response = await self.llm_chat.send_message(user_message)
            return response
        except Exception as e:
            return f"AI analysis error: {str(e)}"
    
    async def generate_recommendations(self, cluster: ClusterInfo) -> List[str]:
        if not self.llm_chat:
            return [
                "Enable cluster autoscaling to optimize node count",
                "Review resource requests and limits for over-provisioning",
                "Consider spot/preemptible instances for non-critical workloads"
            ]
        
        prompt = f"""
        Generate 5 specific, actionable optimization recommendations for this Kubernetes cluster:
        
        Cluster: {cluster.name}
        Provider: {cluster.provider}
        Current monthly cost: ${cluster.total_cost}
        Nodes: {len(cluster.nodes)}
        
        Focus on recommendations that can provide immediate cost savings while maintaining performance.
        Return only the recommendations as a numbered list.
        """
        
        try:
            user_message = UserMessage(text=prompt)
            response = await self.llm_chat.send_message(user_message)
            # Parse recommendations from response
            recommendations = [line.strip() for line in response.split('\
') if line.strip() and any(char.isdigit() for char in line[:3])]
            return recommendations[:5] if recommendations else [
                "Enable horizontal pod autoscaling for better resource utilization",
                "Implement resource quotas to prevent over-provisioning",
                "Use node affinity rules to optimize workload placement",
                "Consider reserved instances for predictable workloads",
                "Implement pod disruption budgets for safer scaling"
            ]
        except Exception as e:
            return [f"AI recommendation error: {str(e)}"]

ai_service = AIAnalysisService()

# Mock data generators
def generate_mock_cluster_nodes(count: int = 5) -> List[ClusterNode]:
    node_types = ["t3.medium", "t3.large", "t3.xlarge", "m5.large", "m5.xlarge"]
    zones = ["us-east-1a", "us-east-1b", "us-east-1c"]
    
    nodes = []
    for i in range(count):
        node_type = random.choice(node_types)
        cpu_capacity = {"t3.medium": 2, "t3.large": 2, "t3.xlarge": 4, "m5.large": 2, "m5.xlarge": 4}[node_type]
        memory_capacity = {"t3.medium": 4, "t3.large": 8, "t3.xlarge": 16, "m5.large": 8, "m5.xlarge": 16}[node_type]
        cost_per_hour = {"t3.medium": 0.0416, "t3.large": 0.0832, "t3.xlarge": 0.1664, "m5.large": 0.096, "m5.xlarge": 0.192}[node_type]
        
        nodes.append(ClusterNode(
            name=f"node-{i+1}",
            cpu_capacity=cpu_capacity,
            memory_capacity=memory_capacity,
            cpu_usage=random.uniform(20, 80),
            memory_usage=random.uniform(30, 85),
            cost_per_hour=cost_per_hour,
            node_type=node_type,
            zone=random.choice(zones),
            status="Ready"
        ))
    
    return nodes

def generate_mock_clusters(count: int = 3) -> List[ClusterInfo]:
    providers = ["AWS", "GCP", "Azure"]
    regions = ["us-east-1", "us-west-2", "europe-west1"]
    
    clusters = []
    for i in range(count):
        nodes = generate_mock_cluster_nodes(random.randint(3, 8))
        total_cost = sum(node.cost_per_hour * 24 * 30 for node in nodes)  # Monthly cost
        
        clusters.append(ClusterInfo(
            name=f"production-cluster-{i+1}",
            provider=random.choice(providers),
            region=random.choice(regions),
            nodes=nodes,
            total_cost=total_cost
        ))
    
    return clusters

# API Endpoints
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "Kubernetes Cost Optimizer API is running"}

@app.get("/api/clusters", response_model=List[ClusterInfo])
async def get_clusters():
    """Get all Kubernetes clusters with cost information"""
    try:
        clusters = await db.clusters.find().to_list(length=None)
        if not clusters:
            # Generate and store mock data
            mock_clusters = generate_mock_clusters()
            for cluster_data in mock_clusters:
                cluster_dict = cluster_data.dict()
                cluster_dict['created_at'] = cluster_dict['created_at'].isoformat()
                for node in cluster_dict['nodes']:
                    node['id'] = node.get('id', str(uuid.uuid4()))
                await db.clusters.insert_one(cluster_dict)
            clusters = await db.clusters.find().to_list(length=None)
        
        return [ClusterInfo(**cluster) for cluster in clusters]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching clusters: {str(e)}")

@app.get("/api/clusters/{cluster_id}", response_model=ClusterInfo)
async def get_cluster(cluster_id: str):
    """Get detailed information about a specific cluster"""
    cluster = await db.clusters.find_one({"id": cluster_id})
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    return ClusterInfo(**cluster)

@app.post("/api/clusters/{cluster_id}/analyze")
async def analyze_cluster(cluster_id: str):
    """Generate AI-powered cost analysis for a cluster"""
    cluster = await db.clusters.find_one({"id": cluster_id})
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    
    cluster_obj = ClusterInfo(**cluster)
    
    # Generate AI analysis
    ai_insights = await ai_service.analyze_cluster_costs(cluster_obj)
    recommendations = await ai_service.generate_recommendations(cluster_obj)
    
    # Calculate potential savings (mock calculation)
    current_utilization = sum(node['cpu_usage'] for node in cluster['nodes']) / len(cluster['nodes'])
    potential_savings = cluster_obj.total_cost * (100 - current_utilization) / 100 * 0.3
    
    analysis = CostAnalysis(
        cluster_id=cluster_id,
        analysis_type="comprehensive",
        recommendations=recommendations,
        potential_savings=potential_savings,
        confidence_score=random.uniform(85, 95),
        ai_insights=ai_insights
    )
    
    # Store analysis
    analysis_dict = analysis.dict()
    analysis_dict['created_at'] = analysis_dict['created_at'].isoformat()
    await db.cost_analyses.insert_one(analysis_dict)
    
    return analysis

@app.get("/api/clusters/{cluster_id}/recommendations", response_model=List[OptimizationRecommendation])
async def get_recommendations(cluster_id: str):
    """Get optimization recommendations for a cluster"""
    cluster = await db.clusters.find_one({"id": cluster_id})
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    
    # Generate mock recommendations
    recommendations = [
        OptimizationRecommendation(
            cluster_id=cluster_id,
            type="rightsizing",
            description="Downsize over-provisioned nodes in zone us-east-1a",
            impact="Reduce costs by optimizing node sizes",
            savings_estimate=450.00,
            implementation_complexity="Medium",
            priority="High"
        ),
        OptimizationRecommendation(
            cluster_id=cluster_id,
            type="scaling",
            description="Enable cluster autoscaling to handle traffic spikes",
            impact="Automatically adjust cluster size based on demand",
            savings_estimate=320.00,
            implementation_complexity="Low",
            priority="High"
        ),
        OptimizationRecommendation(
            cluster_id=cluster_id,
            type="scheduling",
            description="Implement pod affinity rules for better resource utilization",
            impact="Improve workload distribution across nodes",
            savings_estimate=180.00,
            implementation_complexity="High",
            priority="Medium"
        )
    ]
    
    return recommendations

@app.get("/api/dashboard/overview")
async def get_dashboard_overview():
    """Get dashboard overview with key metrics"""
    clusters = await db.clusters.find().to_list(length=None)
    
    if not clusters:
        clusters = [cluster.dict() for cluster in generate_mock_clusters()]
    
    total_clusters = len(clusters)
    total_cost = sum(cluster.get('total_cost', 0) for cluster in clusters)
    total_nodes = sum(len(cluster.get('nodes', [])) for cluster in clusters)
    
    # Calculate average utilization
    all_nodes = []
    for cluster in clusters:
        all_nodes.extend(cluster.get('nodes', []))
    
    avg_cpu_utilization = sum(node.get('cpu_usage', 0) for node in all_nodes) / len(all_nodes) if all_nodes else 0
    avg_memory_utilization = sum(node.get('memory_usage', 0) for node in all_nodes) / len(all_nodes) if all_nodes else 0
    
    # Mock cost trends (last 7 days)
    cost_trends = []
    base_cost = total_cost / 30  # Daily cost
    for i in range(7):
        date = (datetime.now(timezone.utc) - timedelta(days=6-i)).date()
        daily_cost = base_cost * random.uniform(0.9, 1.1)
        cost_trends.append({
            "date": date.isoformat(),
            "cost": round(daily_cost, 2)
        })
    
    return {
        "total_clusters": total_clusters,
        "total_monthly_cost": round(total_cost, 2),
        "total_nodes": total_nodes,
        "avg_cpu_utilization": round(avg_cpu_utilization, 1),
        "avg_memory_utilization": round(avg_memory_utilization, 1),
        "cost_trends": cost_trends,
        "potential_savings": round(total_cost * 0.25, 2),  # Mock 25% potential savings
        "alerts_count": random.randint(2, 8)
    }

@app.get("/api/alerts", response_model=List[AnomalyAlert])
async def get_alerts():
    """Get cost anomaly alerts"""
    alerts = await db.alerts.find().to_list(length=None)
    
    if not alerts:
        # Generate mock alerts
        clusters = await db.clusters.find().to_list(length=None)
        if clusters:
            mock_alerts = []
            for i in range(random.randint(3, 6)):
                cluster = random.choice(clusters)
                alert = AnomalyAlert(
                    cluster_id=cluster['id'],
                    alert_type=random.choice(["cost_spike", "resource_waste", "scaling_issue"]),
                    description=f"Unusual cost pattern detected in {cluster['name']}",
                    severity=random.choice(["low", "medium", "high"])
                )
                mock_alerts.append(alert)
            
            # Store alerts
            for alert in mock_alerts:
                alert_dict = alert.dict()
                alert_dict['detected_at'] = alert_dict['detected_at'].isoformat()
                await db.alerts.insert_one(alert_dict)
            
            alerts = await db.alerts.find().to_list(length=None)
    
    return [AnomalyAlert(**alert) for alert in alerts]

@app.post("/api/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    """Mark an alert as resolved"""
    result = await db.alerts.update_one(
        {"id": alert_id},
        {"$set": {"resolved": True}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {"message": "Alert resolved successfully"}

@app.get("/api/cost-analysis")
async def get_cost_analysis():
    """Get comprehensive cost analysis across all clusters"""
    analyses = await db.cost_analyses.find().to_list(length=None)
    return [CostAnalysis(**analysis) for analysis in analyses]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)