"""
Latency Spike Incident Scenario

A realistic incident scenario with pre-seeded data for tools
"""

INCIDENT = {
    "id": "INC-2024-1029-001",
    "symptom": "API latency spike - p99 latency increased from 200ms to 3000ms",
    "severity": "high",
    "service": "user-api",
    "started_at": "2024-10-29T14:30:00Z",
    "affected_endpoints": [
        "/api/v1/users",
        "/api/v1/users/{id}",
        "/api/v1/users/search"
    ],
    "impact": "50% of user requests experiencing slow response times"
}

# Simulated metrics data
METRICS_DATA = {
    "user-api": {
        "latency_p99": [
            {"timestamp": "14:00", "value": 180},
            {"timestamp": "14:15", "value": 210},
            {"timestamp": "14:30", "value": 2800},  # Spike starts
            {"timestamp": "14:45", "value": 3200},
            {"timestamp": "15:00", "value": 3100},
        ],
        "error_rate": [
            {"timestamp": "14:00", "value": 0.1},
            {"timestamp": "14:15", "value": 0.1},
            {"timestamp": "14:30", "value": 0.2},
            {"timestamp": "14:45", "value": 0.3},
            {"timestamp": "15:00", "value": 0.25},
        ],
        "request_rate": [
            {"timestamp": "14:00", "value": 1200},
            {"timestamp": "14:15", "value": 1150},
            {"timestamp": "14:30", "value": 1180},
            {"timestamp": "14:45", "value": 1220},
            {"timestamp": "15:00", "value": 1190},
        ],
        "database_connections": [
            {"timestamp": "14:00", "value": 45},
            {"timestamp": "14:15", "value": 48},
            {"timestamp": "14:30", "value": 98},  # Near pool limit
            {"timestamp": "14:45", "value": 100}, # Pool exhausted!
            {"timestamp": "15:00", "value": 100},
        ]
    }
}

# Simulated log entries
LOG_ENTRIES = [
    {
        "timestamp": "14:29:45",
        "level": "INFO",
        "message": "Deploying config update: database pool size optimization"
    },
    {
        "timestamp": "14:30:12",
        "level": "WARN",
        "message": "Database connection pool approaching limit (95/100)"
    },
    {
        "timestamp": "14:30:18",
        "level": "ERROR",
        "message": "Database connection pool exhausted - waiting for available connection"
    },
    {
        "timestamp": "14:30:25",
        "level": "ERROR",
        "message": "Query timeout: SELECT * FROM users WHERE id = ? (waited 3000ms for connection)"
    },
    {
        "timestamp": "14:31:00",
        "level": "ERROR",
        "message": "Multiple connection timeouts detected. Connection pool: 100/100 active"
    }
]

# Simulated git history
GIT_HISTORY = [
    {
        "commit": "a3f89d2",
        "timestamp": "14:25:00",
        "author": "deploy-bot",
        "message": "feat: optimize database connection pool configuration",
        "files_changed": ["config/database.yml"],
        "diff": """
-  pool_size: 100
+  pool_size: 50  # Reduced to save memory
-  pool_timeout: 5000
+  pool_timeout: 3000
        """
    },
    {
        "commit": "b7e21a9",
        "timestamp": "13:45:00",
        "author": "jane-dev",
        "message": "refactor: improve user query performance",
        "files_changed": ["src/api/users.py"],
        "diff": """
-  users = db.query(User).filter_by(active=True).all()
+  users = db.query(User).filter_by(active=True).options(joinedload('profile')).all()
        """
    }
]

# The root cause (for validation)
ROOT_CAUSE = {
    "description": "Database connection pool exhaustion due to pool size reduction",
    "trigger": "Config change reduced pool from 100 to 50 connections",
    "contributing_factors": [
        "Recent code change added eager loading (joinedload), increasing connection hold time",
        "No load testing after config change",
        "Pool timeout set too low (3s) causing cascading failures"
    ],
    "solution": "Revert pool size to 100 or increase to 150, adjust timeout to 5s"
}
