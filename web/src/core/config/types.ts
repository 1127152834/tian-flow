export interface ModelConfig {
  basic: string[];
  reasoning: string[];
}

export interface RagConfig {
  provider: string;
}

export interface OlightConfig {
  rag: RagConfig;
  models: ModelConfig;
}
