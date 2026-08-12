# Skills arquivadas

Movidas de `skills/` para `skills-archive/` em 07/08/2026. **Nada foi apagado.**

`skills-archive/` fica fora da árvore que o Claude Code varre: estas skills
custam **zero token** de contexto e não aparecem na lista de sessão. Continuam
no disco e continuam aqui documentadas — é isso que torna arquivar reversível
em vez de perder.

## Restaurar

```bash
mv ~/.claude/skills-archive/<nome> ~/.claude/skills/   # e reinicie o Claude Code
```

O watcher só enxerga diretórios que existiam no início da sessão, então
**reiniciar não é opcional** (ver `docs/manual-registro-agentes-skills.md`).

## Critério usado

Arquivada = sem acoplamento ao material versionado (nenhuma skill, agente,
command ou rule do repo a citava) **e** fora da stack real desta máquina, OU
apontada pelo `doctor_skills.py` como impossível de rotear, OU duplicata
literal de outra. Preservados: as 36 curadas, `gsd-*` (67, integrado a 33
arquivos versionados), `tavily-*` e `hugging-*`.

## Citadas pelo router e nunca construídas (08/08/2026)

Categoria diferente das arquivadas: **estas não estão em `skills-archive/` porque
nunca chegaram a existir.** O `ask-daniel` as citava, o `doctor_router.py` as
acusava, e a citação mandava o Claude para o vazio sem erro. As citações saíram;
o registro fica aqui, que é onde se procura "cadê a skill X".

| nome | o que seria | por que não foi construída |
|---|---|---|
| `trilha-carreira` | mapa de competências de uma carreira ou função — tronco comum + ramos por especialidade, a partir de documentos-fonte, renderizado em grafo HTML + MD do Obsidian + PDF, em `~/trilhas/<trilha>/` | `~/trilhas/` nunca existiu e não há um único artefato de trilha de carreira no disco. Capacidade aspiracional, sem uso em três semanas de trabalho denso |
| `roadmapsh-creator` | publicar uma trilha no site roadmap.sh e minerar os roadmaps oficiais de lá | depende de `trilha-carreira` para ter o que publicar; e o próprio router registrava o custo — ~1 min de clique por nó, achatando os ramos |
| `trilha-builder` | fila de estudo por disciplina (união IGEPP × QConcursos × verticalização) | a capacidade tem quatro donos corretos — `estrategista-concurso` (regra-mãe 8), `concurso-prep`, `~/manual_estudo/disciplinas/README.md` (formato v2) e a regra dura do CLAUDE.md do projeto. Uma quinta cópia seria a única capaz de divergir das outras quatro |

**Gatilhos para reconsiderar.** `trilha-carreira` e `roadmapsh-creator`: quando
houver uma carreira concreta a mapear e um documento-fonte para ela — decisão do
Daniel, e o texto original do router está em `git show 8fe0000^:skills/ask-daniel/SKILL.md`.
`trilha-builder`: se um edital trouxer disciplina nova e for preciso montar trilha
do zero sob o protocolo 72h; aí as peças a fundir são o `disciplinas/README.md` e
o `qconcursos-simulados` (colheita de `subject_ids`, tuning de link por banca).

**Uma saiu desta tabela: a `deep-research` foi construída depois.** Em 08/08/2026 ela
entrou aqui como redundante com o `research-orchestrator`; em 10/08/2026 ela foi
escrita e versionada mesmo assim (`89855ef`), com `SKILL.md` e quatro referências, e
hoje o `apply_skills_archive.py` a barra explicitamente por estar no git. O registro
fica porque a decisão de 08/08 existiu — o que muda é que **a resposta a "cadê a
`deep-research`" passou a ser `skills/deep-research/`**. Corrigido em 11/08/2026,
depois de a linha ter sobrevivido três dias contradizendo o disco e o próprio script.

## Arquivadas depois do lote (decisões individuais)

O lote de 07/08/2026 aplicou o critério de massa. O que vier depois entra aqui com o
seu próprio motivo, porque motivo individual não se lê da tabela de 295.

**`notebooklm` — arquivada em 11/08/2026, por falta de procedência.** É clone de
[`PleasePrompto/notebooklm-skill`](https://github.com/PleasePrompto/notebooklm-skill)
(v1.3.0), trazido em 04/04/2026 como cópia solta: não é plugin, não é symlink para o
submodule, não está no `.gitignore` curado e não aparecia em documento nenhum. O
`CLAUDE.md` manda registrar a procedência de cópia solta justamente para este caso, e
ela nunca foi registrada — este parágrafo paga essa dívida antes de arquivar.

Chegou pesando **218 MB em 1.417 arquivos**. Dos 78 MB de `data/`, o que importava não
era o tamanho: o `browser_state/state.json` guardava **34 cookies** de `.google.com`,
`accounts.google.com` e `notebooklm.google.com`, e o `browser_profile/` ao lado
carregava a mesma sessão autenticada. Uma skill de terceiro, trazida sem procedência,
mantinha sessão viva da conta Google do Daniel parada no disco desde 04/04/2026.

**`data/` foi apagado em 12/08/2026, por decisão dele.** Restam 140 MB, quase todos do
`.venv`. Duas ressalvas ficam registradas porque não se leem do diretório. A primeira
é que **apagar o arquivo local não revoga a sessão no Google** — quem revoga é a
página de segurança da conta, e enquanto isso não for feito o cookie que já vazou (se
vazou) continua valendo. A segunda é que restaurar a skill **não a faz funcionar de
novo**: sem `data/`, ela pede autenticação do zero, e é assim que deve ser.

Voltar continua sendo
`uv run --with pyyaml python scripts/apply_skills_archive.py --restore notebooklm`.

## Índice — 296 skills

| família | qtd |
|---|---|
| `azure-*` | 116 |
| `odoo-*` | 24 |
| `fp-*` | 15 |
| `makepad-*` | 13 |
| `seo-*` | 13 |
| `apify-*` | 12 |
| `threejs-*` | 11 |
| `cc-*` | 8 |
| `conductor-*` | 7 |
| `n8n-*` | 7 |
| `wiki-*` | 7 |
| `fal-*` | 6 |
| `leiloeiro-*` | 6 |
| `startup-*` | 6 |
| `aws-*` | 5 |
| `c4-*` | 5 |
| `robius-*` | 5 |
| `terraform-*` | 5 |
| `angular-*` | 4 |
| `wordpress-*` | 4 |
| `brand-*` | 1 |
| `build-*` | 1 |
| `codebase-*` | 1 |
| `context-*` | 1 |
| `django-*` | 1 |
| `documentation-*` | 1 |
| `error-*` | 1 |
| `ffuf-*` | 1 |
| `food-*` | 1 |
| `hosted-*` | 1 |
| `internal-*` | 1 |
| `performance-*` | 1 |
| `pypict-*` | 1 |
| `sexual-*` | 1 |
| `sharp-*` | 1 |
| `speckit-*` | 1 |

| skill | família | o que fazia |
|---|---|---|
| `angular-best-practices` | angular | "Angular performance optimization and best practices guide. Use when writing, reviewing, or refactoring Angular code for optimal p |
| `angular-migration` | angular | "Migrate from AngularJS to Angular using hybrid mode, incremental component rewriting, and dependency injection updates. Use when  |
| `angular-state-management` | angular | "Master modern Angular state management with Signals, NgRx, and RxJS. Use when setting up global state, managing component stores, |
| `angular-ui-patterns` | angular | "Modern Angular UI patterns for loading states, error handling, and data display. Use when building UI components, handling async  |
| `apify-actor-development` | apify | "Develop, debug, and deploy Apify Actors - serverless cloud programs for web scraping, automation, and data processing. Use when c |
| `apify-actorization` | apify | "Convert existing projects into Apify Actors - serverless cloud programs. Actorize JavaScript/TypeScript (SDK with Actor.init/exit |
| `apify-audience-analysis` | apify | Understand audience demographics, preferences, behavior patterns, and engagement quality across Facebook, Instagram, YouTube, and  |
| `apify-brand-reputation-monitoring` | apify | "Track reviews, ratings, sentiment, and brand mentions across Google Maps, Booking.com, TripAdvisor, Facebook, Instagram, YouTube, |
| `apify-competitor-intelligence` | apify | Analyze competitor strategies, content, pricing, ads, and market positioning across Google Maps, Booking.com, Facebook, Instagram, |
| `apify-content-analytics` | apify | Track engagement metrics, measure campaign ROI, and analyze content performance across Instagram, Facebook, YouTube, and TikTok. |
| `apify-ecommerce` | apify | "Scrape e-commerce data for pricing intelligence, customer reviews, and seller discovery across Amazon, Walmart, eBay, IKEA, and 5 |
| `apify-influencer-discovery` | apify | Find and evaluate influencers for brand partnerships, verify authenticity, and track collaboration performance across Instagram, F |
| `apify-lead-generation` | apify | "Generates B2B/B2C leads by scraping Google Maps, websites, Instagram, TikTok, Facebook, LinkedIn, YouTube, and Google Search. Use |
| `apify-market-research` | apify | Analyze market conditions, geographic opportunities, pricing, consumer behavior, and product validation across Google Maps, Facebo |
| `apify-trend-analysis` | apify | Discover and track emerging trends across Google Trends, Instagram, Facebook, YouTube, and TikTok to inform content strategy. |
| `apify-ultimate-scraper` | apify | "Universal AI-powered web scraper for any platform. Scrape data from Instagram, Facebook, TikTok, YouTube, Google Maps, Google Sea |
| `aws-cost-cleanup` | aws | "Automated cleanup of unused AWS resources to reduce costs" |
| `aws-cost-optimizer` | aws | "Comprehensive AWS cost analysis and optimization recommendations using AWS CLI and Cost Explorer" |
| `aws-penetration-testing` | aws | "This skill should be used when the user asks to \"pentest AWS\", \"test AWS security\", \"enumerate IAM\", \"exploit cloud infras |
| `aws-serverless` | aws | "Specialized skill for building production-ready serverless applications on AWS. Covers Lambda functions, API Gateway, DynamoDB, S |
| `aws-skills` | aws | "AWS development with infrastructure automation and cloud architecture patterns" |
| `azure-ai-agents-persistent-dotnet` | azure | Azure AI Agents Persistent SDK for .NET. Low-level SDK for creating and managing AI agents with threads, messages, runs, and tools |
| `azure-ai-agents-persistent-java` | azure | Azure AI Agents Persistent SDK for Java. Low-level SDK for creating and managing AI agents with threads, messages, runs, and tools |
| `azure-ai-anomalydetector-java` | azure | "Build anomaly detection applications with Azure AI Anomaly Detector SDK for Java. Use when implementing univariate/multivariate a |
| `azure-ai-contentsafety-java` | azure | "Build content moderation applications with Azure AI Content Safety SDK for Java. Use when implementing text/image analysis, block |
| `azure-ai-contentsafety-py` | azure | Azure AI Content Safety SDK for Python. Use for detecting harmful content in text and images with multi-severity classification. |
| `azure-ai-contentsafety-ts` | azure | "Analyze text and images for harmful content using Azure AI Content Safety (@azure-rest/ai-content-safety). Use when moderating us |
| `azure-ai-contentunderstanding-py` | azure | Azure AI Content Understanding SDK for Python. Use for multimodal content extraction from documents, images, audio, and video. |
| `azure-ai-document-intelligence-dotnet` | azure | Azure AI Document Intelligence SDK for .NET. Extract text, tables, and structured data from documents using prebuilt and custom mo |
| `azure-ai-document-intelligence-ts` | azure | "Extract text, tables, and structured data from documents using Azure Document Intelligence (@azure-rest/ai-document-intelligence) |
| `azure-ai-formrecognizer-java` | azure | "Build document analysis applications with Azure Document Intelligence (Form Recognizer) SDK for Java. Use when extracting text, t |
| `azure-ai-ml-py` | azure | Azure Machine Learning SDK v2 for Python. Use for ML workspaces, jobs, models, datasets, compute, and pipelines. |
| `azure-ai-openai-dotnet` | azure | Azure OpenAI SDK for .NET. Client library for Azure OpenAI and OpenAI services. Use for chat completions, embeddings, image genera |
| `azure-ai-projects-dotnet` | azure | Azure AI Projects SDK for .NET. High-level client for Azure AI Foundry projects including agents, connections, datasets, deploymen |
| `azure-ai-projects-java` | azure | Azure AI Projects SDK for Java. High-level SDK for Azure AI Foundry project management including connections, datasets, indexes, a |
| `azure-ai-projects-py` | azure | "Build AI applications using the Azure AI Projects Python SDK (azure-ai-projects). Use when working with Foundry project clients,  |
| `azure-ai-projects-ts` | azure | "Build AI applications using Azure AI Projects SDK for JavaScript (@azure/ai-projects). Use when working with Foundry project clie |
| `azure-ai-textanalytics-py` | azure | Azure AI Text Analytics SDK for sentiment analysis, entity recognition, key phrases, language detection, PII, and healthcare NLP.  |
| `azure-ai-transcription-py` | azure | Azure AI Transcription SDK for Python. Use for real-time and batch speech-to-text transcription with timestamps and diarization. |
| `azure-ai-translation-document-py` | azure | Azure AI Document Translation SDK for batch translation of documents with format preservation. Use for translating Word, PDF, Exce |
| `azure-ai-translation-text-py` | azure | Azure AI Text Translation SDK for real-time text translation, transliteration, language detection, and dictionary lookup. Use for  |
| `azure-ai-translation-ts` | azure | "Build translation applications using Azure Translation SDKs for JavaScript (@azure-rest/ai-translation-text, @azure-rest/ai-trans |
| `azure-ai-vision-imageanalysis-java` | azure | "Build image analysis applications with Azure AI Vision SDK for Java. Use when implementing image captioning, OCR text extraction, |
| `azure-ai-vision-imageanalysis-py` | azure | Azure AI Vision Image Analysis SDK for captions, tags, objects, OCR, people detection, and smart cropping. Use for computer vision |
| `azure-ai-voicelive-dotnet` | azure | Azure AI Voice Live SDK for .NET. Build real-time voice AI applications with bidirectional WebSocket communication. |
| `azure-ai-voicelive-java` | azure | Azure AI VoiceLive SDK for Java. Real-time bidirectional voice conversations with AI assistants using WebSocket. |
| `azure-ai-voicelive-py` | azure | "Build real-time voice AI applications using Azure AI Voice Live SDK (azure-ai-voicelive). Use this skill when creating Python app |
| `azure-ai-voicelive-ts` | azure | Azure AI Voice Live SDK for JavaScript/TypeScript. Build real-time voice AI applications with bidirectional WebSocket communicatio |
| `azure-appconfiguration-java` | azure | Azure App Configuration SDK for Java. Centralized application configuration management with key-value settings, feature flags, and |
| `azure-appconfiguration-py` | azure | Azure App Configuration SDK for Python. Use for centralized configuration management, feature flags, and dynamic settings. |
| `azure-appconfiguration-ts` | azure | "Build applications using Azure App Configuration SDK for JavaScript (@azure/app-configuration). Use when working with configurati |
| `azure-communication-callautomation-java` | azure | "Build call automation workflows with Azure Communication Services Call Automation Java SDK. Use when implementing IVR systems, ca |
| `azure-communication-callingserver-java` | azure | "Azure Communication Services CallingServer (legacy) Java SDK. Note - This SDK is deprecated. Use azure-communication-callautomati |
| `azure-communication-chat-java` | azure | "Build real-time chat applications with Azure Communication Services Chat Java SDK. Use when implementing chat threads, messaging, |
| `azure-communication-common-java` | azure | "Azure Communication Services common utilities for Java. Use when working with CommunicationTokenCredential, user identifiers, tok |
| `azure-communication-sms-java` | azure | "Send SMS messages with Azure Communication Services SMS Java SDK. Use when implementing SMS notifications, alerts, OTP delivery,  |
| `azure-compute-batch-java` | azure | Azure Batch SDK for Java. Run large-scale parallel and HPC batch jobs with pools, jobs, tasks, and compute nodes. |
| `azure-containerregistry-py` | azure | Azure Container Registry SDK for Python. Use for managing container images, artifacts, and repositories. |
| `azure-cosmos-db-py` | azure | "Build Azure Cosmos DB NoSQL services with Python/FastAPI following production-grade patterns. Use when implementing database clie |
| `azure-cosmos-java` | azure | Azure Cosmos DB SDK for Java. NoSQL database operations with global distribution, multi-model support, and reactive patterns. |
| `azure-cosmos-py` | azure | Azure Cosmos DB SDK for Python (NoSQL API). Use for document CRUD, queries, containers, and globally distributed data. |
| `azure-cosmos-rust` | azure | Azure Cosmos DB SDK for Rust (NoSQL API). Use for document CRUD, queries, containers, and globally distributed data. |
| `azure-cosmos-ts` | azure | Azure Cosmos DB JavaScript/TypeScript SDK (@azure/cosmos) for data plane operations. Use for CRUD operations on documents, queries |
| `azure-data-tables-java` | azure | "Build table storage applications with Azure Tables SDK for Java. Use when working with Azure Table Storage or Cosmos DB Table API |
| `azure-data-tables-py` | azure | Azure Tables SDK for Python (Storage and Cosmos DB). Use for NoSQL key-value storage, entity CRUD, and batch operations. |
| `azure-eventgrid-dotnet` | azure | Azure Event Grid SDK for .NET. Client library for publishing and consuming events with Azure Event Grid. Use for event-driven arch |
| `azure-eventgrid-java` | azure | "Build event-driven applications with Azure Event Grid SDK for Java. Use when publishing events, implementing pub/sub patterns, or |
| `azure-eventgrid-py` | azure | Azure Event Grid SDK for Python. Use for publishing events, handling CloudEvents, and event-driven architectures. |
| `azure-eventhub-dotnet` | azure | Azure Event Hubs SDK for .NET. |
| `azure-eventhub-java` | azure | "Build real-time streaming applications with Azure Event Hubs SDK for Java. Use when implementing event streaming, high-throughput |
| `azure-eventhub-py` | azure | Azure Event Hubs SDK for Python streaming. Use for high-throughput event ingestion, producers, consumers, and checkpointing. |
| `azure-eventhub-rust` | azure | Azure Event Hubs SDK for Rust. Use for sending and receiving events, streaming data ingestion. |
| `azure-eventhub-ts` | azure | "Build event streaming applications using Azure Event Hubs SDK for JavaScript (@azure/event-hubs). Use when implementing high-thro |
| `azure-functions` | azure | "Expert patterns for Azure Functions development including isolated worker model, Durable Functions orchestration, cold start opti |
| `azure-identity-dotnet` | azure | Azure Identity SDK for .NET. Authentication library for Azure SDK clients using Microsoft Entra ID. Use for DefaultAzureCredential |
| `azure-identity-java` | azure | "Azure Identity Java SDK for authentication with Azure services. Use when implementing DefaultAzureCredential, managed identity, s |
| `azure-identity-py` | azure | Azure Identity SDK for Python authentication. Use for DefaultAzureCredential, managed identity, service principals, and token cach |
| `azure-identity-rust` | azure | Azure Identity SDK for Rust authentication. Use for DeveloperToolsCredential, ManagedIdentityCredential, ClientSecretCredential, a |
| `azure-identity-ts` | azure | "Authenticate to Azure services using Azure Identity SDK for JavaScript (@azure/identity). Use when configuring authentication wit |
| `azure-keyvault-certificates-rust` | azure | Azure Key Vault Certificates SDK for Rust. Use for creating, importing, and managing certificates. |
| `azure-keyvault-keys-rust` | azure | 'Azure Key Vault Keys SDK for Rust. Use for creating, managing, and using cryptographic keys. Triggers: "keyvault keys rust", "Key |
| `azure-keyvault-keys-ts` | azure | "Manage cryptographic keys using Azure Key Vault Keys SDK for JavaScript (@azure/keyvault-keys). Use when creating, encrypting/dec |
| `azure-keyvault-py` | azure | Azure Key Vault SDK for Python. Use for secrets, keys, and certificates management with secure storage. |
| `azure-keyvault-secrets-rust` | azure | 'Azure Key Vault Secrets SDK for Rust. Use for storing and retrieving secrets, passwords, and API keys. Triggers: "keyvault secret |
| `azure-keyvault-secrets-ts` | azure | "Manage secrets using Azure Key Vault Secrets SDK for JavaScript (@azure/keyvault-secrets). Use when storing and retrieving applic |
| `azure-maps-search-dotnet` | azure | Azure Maps SDK for .NET. Location-based services including geocoding, routing, rendering, geolocation, and weather. Use for addres |
| `azure-messaging-webpubsub-java` | azure | "Build real-time web applications with Azure Web PubSub SDK for Java. Use when implementing WebSocket-based messaging, live update |
| `azure-messaging-webpubsubservice-py` | azure | Azure Web PubSub Service SDK for Python. Use for real-time messaging, WebSocket connections, and pub/sub patterns. |
| `azure-mgmt-apicenter-dotnet` | azure | Azure API Center SDK for .NET. Centralized API inventory management with governance, versioning, and discovery. |
| `azure-mgmt-apicenter-py` | azure | Azure API Center Management SDK for Python. Use for managing API inventory, metadata, and governance across your organization. |
| `azure-mgmt-apimanagement-dotnet` | azure | Azure Resource Manager SDK for API Management in .NET. |
| `azure-mgmt-apimanagement-py` | azure | Azure API Management SDK for Python. Use for managing APIM services, APIs, products, subscriptions, and policies. |
| `azure-mgmt-applicationinsights-dotnet` | azure | Azure Application Insights SDK for .NET. Application performance monitoring and observability resource management. |
| `azure-mgmt-arizeaiobservabilityeval-dotnet` | azure | Azure Resource Manager SDK for Arize AI Observability and Evaluation (.NET). |
| `azure-mgmt-botservice-dotnet` | azure | Azure Resource Manager SDK for Bot Service in .NET. Management plane operations for creating and managing Azure Bot resources, cha |
| `azure-mgmt-botservice-py` | azure | Azure Bot Service Management SDK for Python. Use for creating, managing, and configuring Azure Bot Service resources. |
| `azure-mgmt-fabric-dotnet` | azure | Azure Resource Manager SDK for Fabric in .NET. |
| `azure-mgmt-fabric-py` | azure | Azure Fabric Management SDK for Python. Use for managing Microsoft Fabric capacities and resources. |
| `azure-mgmt-mongodbatlas-dotnet` | azure | "Manage MongoDB Atlas Organizations as Azure ARM resources using Azure.ResourceManager.MongoDBAtlas SDK. Use when creating, updati |
| `azure-mgmt-weightsandbiases-dotnet` | azure | Azure Weights & Biases SDK for .NET. ML experiment tracking and model management via Azure Marketplace. Use for creating W&B insta |
| `azure-microsoft-playwright-testing-ts` | azure | "Run Playwright tests at scale using Azure Playwright Workspaces (formerly Microsoft Playwright Testing). Use when scaling browser |
| `azure-monitor-ingestion-java` | azure | Azure Monitor Ingestion SDK for Java. Send custom logs to Azure Monitor via Data Collection Rules (DCR) and Data Collection Endpoi |
| `azure-monitor-ingestion-py` | azure | Azure Monitor Ingestion SDK for Python. Use for sending custom logs to Log Analytics workspace via Logs Ingestion API. |
| `azure-monitor-opentelemetry-exporter-java` | azure | Azure Monitor OpenTelemetry Exporter for Java. Export OpenTelemetry traces, metrics, and logs to Azure Monitor/Application Insight |
| `azure-monitor-opentelemetry-exporter-py` | azure | Azure Monitor OpenTelemetry Exporter for Python. Use for low-level OpenTelemetry export to Application Insights. |
| `azure-monitor-opentelemetry-py` | azure | Azure Monitor OpenTelemetry Distro for Python. Use for one-line Application Insights setup with auto-instrumentation. |
| `azure-monitor-opentelemetry-ts` | azure | "Instrument applications with Azure Monitor and OpenTelemetry for JavaScript (@azure/monitor-opentelemetry). Use when adding distr |
| `azure-monitor-query-java` | azure | Azure Monitor Query SDK for Java. Execute Kusto queries against Log Analytics workspaces and query metrics from Azure resources. |
| `azure-monitor-query-py` | azure | Azure Monitor Query SDK for Python. Use for querying Log Analytics workspaces and Azure Monitor metrics. |
| `azure-postgres-ts` | azure | Connect to Azure Database for PostgreSQL Flexible Server from Node.js/TypeScript using the pg (node-postgres) package. |
| `azure-resource-manager-cosmosdb-dotnet` | azure | Azure Resource Manager SDK for Cosmos DB in .NET. |
| `azure-resource-manager-durabletask-dotnet` | azure | Azure Resource Manager SDK for Durable Task Scheduler in .NET. |
| `azure-resource-manager-mysql-dotnet` | azure | Azure MySQL Flexible Server SDK for .NET. Database management for MySQL Flexible Server deployments. |
| `azure-resource-manager-playwright-dotnet` | azure | Azure Resource Manager SDK for Microsoft Playwright Testing in .NET. |
| `azure-resource-manager-postgresql-dotnet` | azure | Azure PostgreSQL Flexible Server SDK for .NET. Database management for PostgreSQL Flexible Server deployments. |
| `azure-resource-manager-redis-dotnet` | azure | Azure Resource Manager SDK for Redis in .NET. |
| `azure-resource-manager-sql-dotnet` | azure | Azure Resource Manager SDK for Azure SQL in .NET. |
| `azure-search-documents-dotnet` | azure | Azure AI Search SDK for .NET (Azure.Search.Documents). Use for building search applications with full-text, vector, semantic, and  |
| `azure-search-documents-py` | azure | Azure AI Search SDK for Python. Use for vector search, hybrid search, semantic ranking, indexing, and skillsets. |
| `azure-search-documents-ts` | azure | "Build search applications using Azure AI Search SDK for JavaScript (@azure/search-documents). Use when creating/managing indexes, |
| `azure-security-keyvault-keys-dotnet` | azure | Azure Key Vault Keys SDK for .NET. Client library for managing cryptographic keys in Azure Key Vault and Managed HSM. Use for key  |
| `azure-security-keyvault-keys-java` | azure | "Azure Key Vault Keys Java SDK for cryptographic key management. Use when creating, managing, or using RSA/EC keys, performing enc |
| `azure-security-keyvault-secrets-java` | azure | "Azure Key Vault Secrets Java SDK for secret management. Use when storing, retrieving, or managing passwords, API keys, connection |
| `azure-servicebus-dotnet` | azure | Azure Service Bus SDK for .NET. Enterprise messaging with queues, topics, subscriptions, and sessions. |
| `azure-servicebus-py` | azure | Azure Service Bus SDK for Python messaging. Use for queues, topics, subscriptions, and enterprise messaging patterns. |
| `azure-servicebus-ts` | azure | "Build messaging applications using Azure Service Bus SDK for JavaScript (@azure/service-bus). Use when implementing queues, topic |
| `azure-speech-to-text-rest-py` | azure | Azure Speech to Text REST API for short audio (Python). Use for simple speech recognition of audio files up to 60 seconds without  |
| `azure-storage-blob-java` | azure | "Build blob storage applications with Azure Storage Blob SDK for Java. Use when uploading, downloading, or managing files in Azure |
| `azure-storage-blob-py` | azure | Azure Blob Storage SDK for Python. Use for uploading, downloading, listing blobs, managing containers, and blob lifecycle. |
| `azure-storage-blob-rust` | azure | Azure Blob Storage SDK for Rust. Use for uploading, downloading, and managing blobs and containers. |
| `azure-storage-blob-ts` | azure | Azure Blob Storage JavaScript/TypeScript SDK (@azure/storage-blob) for blob operations. Use for uploading, downloading, listing, a |
| `azure-storage-file-datalake-py` | azure | Azure Data Lake Storage Gen2 SDK for Python. Use for hierarchical file systems, big data analytics, and file/directory operations. |
| `azure-storage-file-share-py` | azure | Azure Storage File Share SDK for Python. Use for SMB file shares, directories, and file operations in the cloud. |
| `azure-storage-file-share-ts` | azure | Azure File Share JavaScript/TypeScript SDK (@azure/storage-file-share) for SMB file share operations. |
| `azure-storage-queue-py` | azure | Azure Queue Storage SDK for Python. Use for reliable message queuing, task distribution, and asynchronous processing. |
| `azure-storage-queue-ts` | azure | Azure Queue Storage JavaScript/TypeScript SDK (@azure/storage-queue) for message queue operations. Use for sending, receiving, pee |
| `azure-web-pubsub-ts` | azure | "Build real-time messaging applications using Azure Web PubSub SDKs for JavaScript (@azure/web-pubsub, @azure/web-pubsub-client).  |
| `brand-guidelines-community` | brand | "Applies Anthropic's official brand colors and typography to any sort of artifact that may benefit from having Anthropic's look-an |
| `build` | build | build |
| `c4-architecture-c4-architecture` | c4 | "Generate comprehensive C4 architecture documentation for an existing repository/codebase using a bottom-up analysis approach." |
| `c4-code` | c4 | Expert C4 Code-level documentation specialist. Analyzes code directories to create comprehensive C4 code-level documentation inclu |
| `c4-component` | c4 | Expert C4 Component-level documentation specialist. Synthesizes C4 Code-level documentation into Component-level architecture, def |
| `c4-container` | c4 | Expert C4 Container-level documentation specialist. |
| `c4-context` | c4 | Expert C4 Context-level documentation specialist. Creates high-level system context diagrams, documents personas, user journeys, s |
| `cc-skill-backend-patterns` | cc | "Backend architecture patterns, API design, database optimization, and server-side best practices for Node.js, Express, and Next.j |
| `cc-skill-clickhouse-io` | cc | "ClickHouse database patterns, query optimization, analytics, and data engineering best practices for high-performance analytical  |
| `cc-skill-coding-standards` | cc | "Universal coding standards, best practices, and patterns for TypeScript, JavaScript, React, and Node.js development." |
| `cc-skill-continuous-learning` | cc | "Development skill from everything-claude-code" |
| `cc-skill-frontend-patterns` | cc | "Frontend development patterns for React, Next.js, state management, performance optimization, and UI best practices." |
| `cc-skill-project-guidelines-example` | cc | "Project Guidelines Skill (Example)" |
| `cc-skill-security-review` | cc | "Use this skill when adding authentication, handling user input, working with secrets, creating API endpoints, or implementing pay |
| `cc-skill-strategic-compact` | cc | "Development skill from everything-claude-code" |
| `codebase-cleanup-tech-debt` | codebase | "You are a technical debt expert specializing in identifying, quantifying, and prioritizing technical debt in software projects. A |
| `conductor-implement` | conductor | "Execute tasks from a track's implementation plan following TDD workflow" |
| `conductor-manage` | conductor | "Manage track lifecycle: archive, restore, delete, rename, and cleanup" |
| `conductor-new-track` | conductor | "Create a new track with specification and phased implementation plan" |
| `conductor-revert` | conductor | "Git-aware undo by logical work unit (track, phase, or task)" |
| `conductor-setup` | conductor | Configure a Rails project to work with Conductor (parallel coding agents) allowed-tools: Bash(chmod *), Bash(bundle *), Bash(npm * |
| `conductor-status` | conductor | "Display project status, active tracks, and next actions" |
| `conductor-validator` | conductor | 'Validates Conductor project artifacts for completeness, consistency, and correctness. Use after setup, when diagnosing issues, or |
| `context-management-context-restore` | context | "Use when working with context management context restore" |
| `django-access-review` | django | django-access-review |
| `documentation-generation-doc-generate` | documentation | "You are a documentation expert specializing in creating comprehensive, maintainable documentation from code. Generate API docs, a |
| `error-diagnostics-error-analysis` | error | "You are an expert error analysis specialist with deep expertise in debugging distributed systems, analyzing production incidents, |
| `fal-audio` | fal | "Text-to-speech and speech-to-text using fal.ai audio models" |
| `fal-generate` | fal | "Generate images and videos using fal.ai AI models" |
| `fal-image-edit` | fal | "AI-powered image editing with style transfer and object removal" |
| `fal-platform` | fal | "Platform APIs for model management, pricing, and usage tracking" |
| `fal-upscale` | fal | "Upscale and enhance image and video resolution using AI" |
| `fal-workflow` | fal | "Generate workflow JSON files for chaining AI models" |
| `ffuf-claude-skill` | ffuf | "Web fuzzing with ffuf" |
| `food-database-query` | food | Food Database Query |
| `fp-async` | fp | Practical async patterns using TaskEither - clean pipelines instead of try/catch hell, with real API examples |
| `fp-backend` | fp | Functional programming patterns for Node.js/Deno backend development using fp-ts, ReaderTaskEither, and functional dependency inje |
| `fp-data-transforms` | fp | Everyday data transformations using functional patterns - arrays, objects, grouping, aggregation, and null-safe access |
| `fp-either-ref` | fp | Quick reference for Either type. Use when user needs error handling, validation, or operations that can fail with typed errors. |
| `fp-errors` | fp | Stop throwing everywhere - handle errors as values using Either and TaskEither for cleaner, more predictable code |
| `fp-option-ref` | fp | Quick reference for Option type. Use when user needs to handle nullable values, optional data, or wants to avoid null checks. |
| `fp-pipe-ref` | fp | Quick reference for pipe and flow. Use when user needs to chain functions, compose operations, or build data pipelines in fp-ts. |
| `fp-pragmatic` | fp | A practical, jargon-free guide to functional programming - the 80/20 approach that gets results without the academic overhead |
| `fp-react` | fp | Practical patterns for using fp-ts with React - hooks, state, forms, data fetching. Works with React 18/19, Next.js 14/15. |
| `fp-refactor` | fp | Comprehensive guide for refactoring imperative TypeScript code to fp-ts functional patterns |
| `fp-taskeither-ref` | fp | Quick reference for TaskEither. Use when user needs async error handling, API calls, or Promise-based operations that can fail. |
| `fp-ts-errors` | fp | "Handle errors as values using fp-ts Either and TaskEither for cleaner, more predictable TypeScript code. Use when implementing er |
| `fp-ts-pragmatic` | fp | "A practical, jargon-free guide to fp-ts functional programming - the 80/20 approach that gets results without the academic overhe |
| `fp-ts-react` | fp | "Practical patterns for using fp-ts with React - hooks, state, forms, data fetching. Use when building React apps with functional  |
| `fp-types-ref` | fp | Quick reference for fp-ts types. Use when user asks which type to use, needs Option/Either/Task decision help, or wants fp-ts impo |
| `hosted-agents-v2-py` | hosted | "Build hosted agents using Azure AI Projects SDK with ImageBasedHostedAgentDefinition. Use when creating container-based agents in |
| `internal-comms-community` | internal | "A set of resources to help me write all kinds of internal communications, using the formats that my company likes to use. Claude  |
| `leiloeiro-avaliacao` | leiloeiro | Avaliacao pericial de imoveis em leilao. Valor de mercado, liquidacao forcada, ABNT NBR 14653, metodos comparativo/renda/custo, CU |
| `leiloeiro-edital` | leiloeiro | Analise e auditoria de editais de leilao judicial e extrajudicial. Riscos ocultos, clausulas perigosas, debitos, ocupante e classi |
| `leiloeiro-ia` | leiloeiro | Especialista em leiloes judiciais e extrajudiciais de imoveis. Analise juridica, pericial e de mercado integrada. Orquestra os 5 m |
| `leiloeiro-juridico` | leiloeiro | 'Analise juridica de leiloes: nulidades, bem de familia, alienacao fiduciaria, CPC arts 829-903, Lei 9514/97, onus reais, embargos |
| `leiloeiro-mercado` | leiloeiro | Analise de mercado imobiliario para leiloes. Liquidez, desagio tipico, ROI, estrategias de saida (flip/reforma/renda), Selic 2025  |
| `leiloeiro-risco` | leiloeiro | Analise de risco em leiloes de imoveis. Score 36 pontos, riscos juridicos/financeiros/operacionais, stress test 4 cenarios e ROI p |
| `makepad-animation` | makepad | / CRITICAL: Use for Makepad animation system. Triggers on: makepad animation, makepad animator, makepad hover, makepad state, make |
| `makepad-basics` | makepad | / CRITICAL: Use for Makepad getting started and app structure. Triggers on: makepad, makepad getting started, makepad tutorial, li |
| `makepad-deployment` | makepad | / CRITICAL: Use for Makepad packaging and deployment. Triggers on: deploy, package, APK, IPA, 打包, 部署, cargo-packager, cargo-makepa |
| `makepad-dsl` | makepad | / CRITICAL: Use for Makepad DSL syntax and inheritance. Triggers on: makepad dsl, live_design, makepad inheritance, makepad protot |
| `makepad-event-action` | makepad | / CRITICAL: Use for Makepad event and action handling. Triggers on: makepad event, makepad action, Event enum, ActionTrait, handle |
| `makepad-font` | makepad | / CRITICAL: Use for Makepad font and text rendering. Triggers on: makepad font, makepad text, makepad glyph, makepad typography, f |
| `makepad-layout` | makepad | / CRITICAL: Use for Makepad layout system. Triggers on: makepad layout, makepad width, makepad height, makepad flex, makepad paddi |
| `makepad-platform` | makepad | / CRITICAL: Use for Makepad cross-platform support. Triggers on: makepad platform, makepad os, makepad macos, makepad windows, mak |
| `makepad-reference` | makepad | / CRITICAL: Use for Makepad troubleshooting and reference. Triggers on: troubleshoot, error, debug, fix, problem, issue, no matchi |
| `makepad-shaders` | makepad | / CRITICAL: Use for Makepad shader system. Triggers on: makepad shader, makepad draw_bg, Sdf2d, makepad pixel, makepad glsl, makep |
| `makepad-skills` | makepad | "Makepad UI development skills for Rust apps: setup, patterns, shaders, packaging, and troubleshooting." |
| `makepad-splash` | makepad | / CRITICAL: Use for Makepad Splash scripting language. Triggers on: splash language, makepad script, makepad scripting, script!, c |
| `makepad-widgets` | makepad | / CRITICAL: Use for Makepad widgets and UI components. Triggers on: makepad widget, makepad View, makepad Button, makepad Label, m |
| `n8n-code-javascript` | n8n | Write JavaScript code in n8n Code nodes. Use when writing JavaScript in n8n, using $input/$json/$node syntax, making HTTP requests |
| `n8n-code-python` | n8n | Write Python code in n8n Code nodes. Use when writing Python in n8n, using _input/_json/_node syntax, working with standard librar |
| `n8n-expression-syntax` | n8n | Validate n8n expression syntax and fix common errors. Use when writing n8n expressions, using {{}} syntax, accessing $json/$node v |
| `n8n-mcp-tools-expert` | n8n | Expert guide for using n8n-mcp MCP tools effectively. Use when searching for nodes, validating configurations, accessing templates |
| `n8n-node-configuration` | n8n | Operation-aware node configuration guidance. Use when configuring nodes, understanding property dependencies, determining required |
| `n8n-validation-expert` | n8n | Interpret validation errors and guide fixing them. Use when encountering validation errors, validation warnings, false positives,  |
| `n8n-workflow-patterns` | n8n | Proven workflow architectural patterns from real n8n workflows. Use when building new workflows, designing workflow structure, cho |
| `notebooklm` | — | Consulta cadernos do Google NotebookLM por automação de navegador, com respostas ancoradas nas fontes. Arquivada em 11/08/2026 — ver "Arquivadas depois do lote" |
| `odoo-accounting-setup` | odoo | "Expert guide for configuring Odoo Accounting: chart of accounts, journals, fiscal positions, taxes, payment terms, and bank recon |
| `odoo-automated-tests` | odoo | "Write and run Odoo automated tests using TransactionCase, HttpCase, and browser tour tests. Covers test data setup, mocking, and  |
| `odoo-backup-strategy` | odoo | "Complete Odoo backup and restore strategy: database dumps, filestore backup, automated scheduling, cloud storage upload, and test |
| `odoo-docker-deployment` | odoo | "Production-ready Docker and docker-compose setup for Odoo with PostgreSQL, persistent volumes, environment-based configuration, a |
| `odoo-ecommerce-configurator` | odoo | "Expert guide for Odoo eCommerce and Website: product catalog, payment providers, shipping methods, SEO, and order-to-fulfillment  |
| `odoo-edi-connector` | odoo | "Guide for implementing EDI (Electronic Data Interchange) with Odoo: X12, EDIFACT document mapping, partner onboarding, and automa |
| `odoo-hr-payroll-setup` | odoo | "Expert guide for Odoo HR and Payroll: salary structures, payslip rules, leave policies, employee contracts, and payroll journal e |
| `odoo-inventory-optimizer` | odoo | "Expert guide for Odoo Inventory: stock valuation (FIFO/AVCO), reordering rules, putaway strategies, routes, and multi-warehouse c |
| `odoo-l10n-compliance` | odoo | "Country-specific Odoo localization: tax configuration, e-invoicing (CFDI, FatturaPA, SAF-T), fiscal reporting, and country chart  |
| `odoo-manufacturing-advisor` | odoo | "Expert guide for Odoo Manufacturing: Bills of Materials (BoM), Work Centers, routings, MRP planning, and production order workflo |
| `odoo-migration-helper` | odoo | "Step-by-step guide for migrating Odoo custom modules between versions (v14→v15→v16→v17). Covers API changes, deprecated methods,  |
| `odoo-module-developer` | odoo | "Expert guide for creating custom Odoo modules. Covers __manifest__.py, model inheritance, ORM patterns, and module structure best |
| `odoo-orm-expert` | odoo | "Master Odoo ORM patterns: search, browse, create, write, domain filters, computed fields, and performance-safe query techniques." |
| `odoo-performance-tuner` | odoo | "Expert guide for diagnosing and fixing Odoo performance issues: slow queries, worker configuration, memory limits, PostgreSQL tun |
| `odoo-project-timesheet` | odoo | "Expert guide for Odoo Project and Timesheets: task stages, billable time tracking, timesheet approval, budget alerts, and invoici |
| `odoo-purchase-workflow` | odoo | "Expert guide for Odoo Purchase: RFQ → PO → Receipt → Vendor Bill workflow, purchase agreements, vendor price lists, and 3-way mat |
| `odoo-qweb-templates` | odoo | "Expert in Odoo QWeb templating for PDF reports, email templates, and website pages. Covers t-if, t-foreach, t-field, and report a |
| `odoo-rpc-api` | odoo | "Expert on Odoo's external JSON-RPC and XML-RPC APIs. Covers authentication, model calls, record CRUD, and real-world integration  |
| `odoo-sales-crm-expert` | odoo | "Expert guide for Odoo Sales and CRM: pipeline stages, quotation templates, pricelists, sales teams, lead scoring, and forecasting |
| `odoo-security-rules` | odoo | "Expert in Odoo access control: ir.model.access.csv, record rules (ir.rule), groups, and multi-company security patterns." |
| `odoo-shopify-integration` | odoo | "Connect Odoo with Shopify: sync products, inventory, orders, and customers using the Shopify API and Odoo's external API or conne |
| `odoo-upgrade-advisor` | odoo | "Step-by-step Odoo version upgrade advisor: pre-upgrade checklist, community vs enterprise upgrade path, OCA module compatibility, |
| `odoo-woocommerce-bridge` | odoo | "Sync Odoo with WooCommerce: products, inventory, orders, and customers via WooCommerce REST API and Odoo external API." |
| `odoo-xml-views-builder` | odoo | "Expert at building Odoo XML views: Form, List, Kanban, Search, Calendar, and Graph. Generates correct XML for Odoo 14-17 with pro |
| `performance-testing-review-multi-agent-review` | performance | "Use when working with performance testing review multi agent review" |
| `pypict-skill` | pypict | "Pairwise test generation" |
| `robius-app-architecture` | robius | / CRITICAL: Use for Robius app architecture patterns. Triggers on: Tokio, async, submit_async_request, 异步, 架构, SignalToUI, Cx::pos |
| `robius-event-action` | robius | / CRITICAL: Use for Robius event and action patterns. Triggers on: custom action, MatchEvent, post_action, cx.widget_action, handl |
| `robius-matrix-integration` | robius | / CRITICAL: Use for Matrix SDK integration with Makepad. Triggers on: Matrix SDK, sliding sync, MatrixRequest, timeline, matrix-sd |
| `robius-state-management` | robius | / CRITICAL: Use for Robius state management patterns. Triggers on: AppState, persistence, theme switch, 状态管理, Scope::with_data, sa |
| `robius-widget-patterns` | robius | / CRITICAL: Use for Robius widget patterns. Triggers on: apply_over, TextOrImage, modal, 可复用, 模态, collapsible, drag drop, reusable |
| `seo-audit` | seo | Diagnose and audit SEO issues affecting crawlability, indexation, rankings, and organic performance. |
| `seo-authority-builder` | seo | 'Analyzes content for E-E-A-T signals and suggests improvements to build authority and trust. Identifies missing credibility eleme |
| `seo-cannibalization-detector` | seo | Analyzes multiple provided pages to identify keyword overlap and potential cannibalization issues. Suggests differentiation strate |
| `seo-content-auditor` | seo | Analyzes provided content for quality, E-E-A-T signals, and SEO best practices. Scores content and provides improvement recommenda |
| `seo-content-planner` | seo | 'Creates comprehensive content outlines and topic clusters for SEO. Plans content calendars and identifies topic gaps. Use PROACTI |
| `seo-content-refresher` | seo | Identifies outdated elements in provided content and suggests updates to maintain freshness. Finds statistics, dates, and examples |
| `seo-content-writer` | seo | Writes SEO-optimized content based on provided keywords and topic briefs. Creates engaging, comprehensive content following best p |
| `seo-forensic-incident-response` | seo | "Investigate sudden drops in organic traffic or rankings and run a structured forensic SEO incident response with triage, root-cau |
| `seo-fundamentals` | seo | Core principles of SEO including E-E-A-T, Core Web Vitals, technical foundations, content quality, and how modern search engines e |
| `seo-keyword-strategist` | seo | Analyzes keyword usage in provided content, calculates density, suggests semantic variations and LSI keywords based on the topic.  |
| `seo-meta-optimizer` | seo | Creates optimized meta titles, descriptions, and URL suggestions based on character limits and best practices. Generates compellin |
| `seo-snippet-hunter` | seo | Formats content to be eligible for featured snippets and SERP features. Creates snippet-optimized content blocks based on best pra |
| `seo-structure-architect` | seo | Analyzes and optimizes content structure including header hierarchy, suggests schema markup, and internal linking opportunities. C |
| `sexual-health-analyzer` | sexual | Sexual Health Analyzer |
| `sharp-edges` | sharp | sharp-edges |
| `speckit-updater` | speckit | SpecKit Safe Update |
| `startup-analyst` | startup | Expert startup business analyst specializing in market sizing, financial modeling, competitive analysis, and strategic planning fo |
| `startup-business-analyst-business-case` | startup | 'Generate comprehensive investor-ready business case document with market, solution, financials, and strategy ' |
| `startup-business-analyst-financial-projections` | startup | 'Create detailed 3-5 year financial model with revenue, costs, cash flow, and scenarios ' |
| `startup-business-analyst-market-opportunity` | startup | 'Generate comprehensive market opportunity analysis with TAM/SAM/SOM calculations ' |
| `startup-financial-modeling` | startup | This skill should be used when the user asks to \\\"create financial projections", "build a financial model", "forecast revenue",  |
| `startup-metrics-framework` | startup | This skill should be used when the user asks about \\\"key startup metrics", "SaaS metrics", "CAC and LTV", "unit economics", "bur |
| `terraform-aws-modules` | terraform | "Terraform module creation for AWS — reusable modules, state management, and HCL best practices. Use when building or reviewing Te |
| `terraform-infrastructure` | terraform | "Terraform infrastructure as code workflow for provisioning cloud resources, creating reusable modules, and managing infrastructur |
| `terraform-module-library` | terraform | "Build reusable Terraform modules for AWS, Azure, and GCP infrastructure following infrastructure-as-code best practices. Use when |
| `terraform-skill` | terraform | "Terraform infrastructure as code best practices" |
| `terraform-specialist` | terraform | Expert Terraform/OpenTofu specialist mastering advanced IaC automation, state management, and enterprise infrastructure patterns. |
| `threejs-animation` | threejs | Three.js animation - keyframe animation, skeletal animation, morph targets, animation mixing. Use when animating objects, playing  |
| `threejs-fundamentals` | threejs | Three.js scene setup, cameras, renderer, Object3D hierarchy, coordinate systems. Use when setting up 3D scenes, creating cameras,  |
| `threejs-geometry` | threejs | Three.js geometry creation - built-in shapes, BufferGeometry, custom geometry, instancing. Use when creating 3D shapes, working wi |
| `threejs-interaction` | threejs | Three.js interaction - raycasting, controls, mouse/touch input, object selection. Use when handling user input, implementing click |
| `threejs-lighting` | threejs | Three.js lighting - light types, shadows, environment lighting. Use when adding lights, configuring shadows, setting up IBL, or op |
| `threejs-loaders` | threejs | Three.js asset loading - GLTF, textures, images, models, async patterns. Use when loading 3D models, textures, HDR environments, o |
| `threejs-materials` | threejs | Three.js materials - PBR, basic, phong, shader materials, material properties. Use when styling meshes, working with textures, cre |
| `threejs-postprocessing` | threejs | Three.js post-processing - EffectComposer, bloom, DOF, screen effects. Use when adding visual effects, color grading, blur, glow,  |
| `threejs-shaders` | threejs | Three.js shaders - GLSL, ShaderMaterial, uniforms, custom effects. Use when creating custom visual effects, modifying vertices, wr |
| `threejs-skills` | threejs | "Create 3D scenes, interactive experiences, and visual effects using Three.js. Use when user requests 3D graphics, WebGL experienc |
| `threejs-textures` | threejs | Three.js textures - texture types, UV mapping, environment maps, texture settings. Use when working with images, UV coordinates, c |
| `wiki-architect` | wiki | "Analyzes code repositories and generates hierarchical documentation structures with onboarding guides. Use when the user wants to |
| `wiki-changelog` | wiki | "Analyzes git commit history and generates structured changelogs categorized by change type. Use when the user asks about recent c |
| `wiki-onboarding` | wiki | "Generates two complementary onboarding guides \u2014 a Principal-Level architectural deep-dive and a Zero-to-Hero contributor wal |
| `wiki-page-writer` | wiki | "Generates rich technical documentation pages with dark-mode Mermaid diagrams, source code citations, and first-principles depth.  |
| `wiki-qa` | wiki | "Answers questions about a code repository using source file analysis. Use when the user asks a question about how something works |
| `wiki-researcher` | wiki | "Conducts multi-turn iterative deep research on specific topics within a codebase with zero tolerance for shallow analysis. Use wh |
| `wiki-vitepress` | wiki | "Packages generated wiki Markdown into a VitePress static site with dark theme, dark-mode Mermaid diagrams with click-to-zoom, and |
| `wordpress-penetration-testing` | wordpress | "This skill should be used when the user asks to \"pentest WordPress sites\", \"scan WordPress for vulnerabilities\", \"enumerate  |
| `wordpress-plugin-development` | wordpress | "WordPress plugin development workflow covering plugin architecture, hooks, admin interfaces, REST API, and security best practice |
| `wordpress-theme-development` | wordpress | "WordPress theme development workflow covering theme architecture, template hierarchy, custom post types, block editor support, an |
| `wordpress-woocommerce-development` | wordpress | "WooCommerce store development workflow covering store setup, payment integration, shipping configuration, and customization." |
