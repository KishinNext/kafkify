# Kafka Producer & Consumer - Arquitectura de Dos Servidores

Este proyecto implementa un sistema de productor y consumidor de Kafka usando FastAPI, con dos servidores separados que corren en paralelo sin bloquearse.

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                     Sistema Kafka                               │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────┐          ┌─────────────────────────┐
│  Servidor Productor     │          │  Servidor Consumidor    │
│  (Puerto 8000)          │          │  (Puerto 8001)          │
│                         │          │                         │
│  POST /producers/...    │          │  GET /consumers/status  │
│  ↓                      │          │  GET /consumers/messages│
│  Envía mensajes a Kafka │ ────────→│  ↓                      │
└─────────────────────────┘          │  Consume en background  │
                                     └─────────────────────────┘
         ↓                                      ↑
         └──────────→  Kafka Broker  ←──────────┘
                    (Docker Container)
```

- **Servidor Productor** (puerto 8000): API REST para enviar mensajes a Kafka
- **Servidor Consumidor** (puerto 8001): Consume mensajes en background de forma continua y los almacena en memoria

## 📋 Requisitos Previos

### Instalar Just (task runner)

```bash
brew install just
```

### Instalar jq (para formatear JSON)

```bash
brew install jq
```

### Instalar dependencias Python

```bash
pip install uv
uv sync
```

## 🚀 Cómo Usar

### 1. Iniciar Kafka (Docker)

```bash
docker-compose up -d
```

### 2. Iniciar los Servidores (en terminales separadas)

**Terminal 1 - Productor:**

```bash
just run-producer
# O directamente: python main_producer.py
```

El servidor del productor estará disponible en: http://localhost:8000

**Terminal 2 - Consumidor:**

```bash
just run-consumer
# O directamente: python main_consumer.py
```

El servidor del consumidor estará disponible en: http://localhost:8001

> **Nota:** Ambos servidores deben estar corriendo al mismo tiempo para que funcionen correctamente.

### 3. Verificar que los servidores están activos

```bash
# Health check del productor
just health-producer

# Health check del consumidor
just health-consumer
```

### 4. Producir mensajes

Crear 10 personas (mensajes):

```bash
just create-people 10
```

Crear 100 personas:

```bash
just create-people 100
```

### 5. Ver mensajes consumidos

Ver estado del consumidor:

```bash
just consumer-status
```

Ver últimos 10 mensajes consumidos:

```bash
just consumer-messages
```

Ver últimos 50 mensajes:

```bash
just consumer-messages 50
```

## 🔌 Endpoints Disponibles

### Productor (puerto 8000)

- `GET /health-check` - Verificar estado del servidor
- `POST /producers/basic_producer?number_of_people=N` - Crear N mensajes
- `GET /docs` - Documentación interactiva Swagger

### Consumidor (puerto 8001)

- `GET /health-check` - Verificar estado del servidor
- `GET /consumers/status` - Ver estado del consumidor
- `GET /consumers/messages?limit=N` - Ver últimos N mensajes consumidos
- `POST /consumers/stop` - Detener el consumidor temporalmente
- `POST /consumers/start` - Reiniciar el consumidor
- `GET /docs` - Documentación interactiva Swagger

## 🛑 Detener todo

```bash
# Ctrl+C en ambas terminales para detener los servidores

# Detener Kafka
docker-compose down
```

## 📝 Comandos Just Disponibles

```bash
just run-producer         # Iniciar servidor productor
just run-consumer         # Iniciar servidor consumidor
just health-producer      # Health check productor
just health-consumer      # Health check consumidor
just create-people N      # Crear N mensajes
just consumer-status      # Ver estado del consumidor
just consumer-messages N  # Ver últimos N mensajes
just consumer-stop        # Detener consumidor
just consumer-start       # Iniciar consumidor
```

## 💡 Ventajas de esta Arquitectura

1. **No hay bloqueos**: Cada servidor corre independientemente
2. **Escalabilidad**: Puedes ejecutar múltiples instancias de cada servidor
3. **Flexibilidad**: Puedes detener/iniciar cada servicio sin afectar al otro
4. **Monitoreo**: APIs dedicadas para ver el estado de cada componente
5. **Desarrollo**: Más fácil de debuggear y desarrollar cada parte por separado
