import {
  IconBolt,
  IconBrandAws,
  IconBrandCoinbase,
  IconBrandGoogle,
  IconBrandOpenai,
  IconDevices2,
  IconLetterA,
  IconLetterT,
  IconRobot,
  IconUsers,
} from '@tabler/icons-react';
import ollamaUrl from '../../../assets/ollama.jpg';
import openaiUrl from '../../../assets/openai.jpg';
import geminiUrl from '../../../assets/gemini.jpg';
import anthropicUrl from '../../../assets/anthropic.jpg';
import cohereUrl from '../../../assets/cohere.jpg';
import togetherUrl from '../../../assets/together.jpg';
import bedrockUrl from '../../../assets/bedrock.jpg';
import customUrl from '../../../assets/custom.jpg';

export type JudgeType =
  | 'human'
  | 'ollama'
  | 'openai'
  | 'gemini'
  | 'anthropic'
  | 'cohere'
  | 'together'
  | 'bedrock'
  | 'groq'
  | 'custom';

export function judgeTypeIconComponent(judgeType: JudgeType) {
  // TODO: get SVGs for real Ollama, Anthropic, Cohere, Groq, and Together logos
  switch (judgeType) {
    case 'human':
      return IconUsers;
    case 'ollama':
      return IconDevices2;
    case 'openai':
      return IconBrandOpenai;
    case 'gemini':
      return IconBrandGoogle;
    case 'anthropic':
      return IconLetterA;
    case 'cohere':
      return IconBrandCoinbase;
    case 'together':
      return IconLetterT;
    case 'bedrock':
      return IconBrandAws;
    case 'groq':
      return IconBolt;
    case 'custom':
    default:
      return IconRobot;
  }
}

export function judgeTypeToCoverImageUrl(judgeType: JudgeType) {
  switch (judgeType) {
    case 'ollama':
      return ollamaUrl;
    case 'openai':
      return openaiUrl;
    case 'gemini':
      return geminiUrl;
    case 'anthropic':
      return anthropicUrl;
    case 'cohere':
      return cohereUrl;
    case 'together':
      return togetherUrl;
    case 'bedrock':
      return bedrockUrl;
    case 'groq':
      return bedrockUrl; // TODO
    case 'custom':
      return customUrl;
    case 'human':
    default:
      return;
  }
}

export function judgeTypeToHumanReadableName(judgeType: JudgeType) {
  switch (judgeType) {
    case 'ollama':
      return 'Ollama';
    case 'openai':
      return 'OpenAI';
    case 'gemini':
      return 'Gemini';
    case 'anthropic':
      return 'Anthropic';
    case 'human':
      return 'Human';
    case 'cohere':
      return 'Cohere';
    case 'together':
      return 'Together AI';
    case 'bedrock':
      return 'AWS Bedrock';
    case 'groq':
      return 'Groq';
    case 'custom':
      return 'Custom Fine-Tune';
    default:
      return judgeType;
  }
}

export function judgeTypeToApiKeyName(judgeType: JudgeType) {
  switch (judgeType) {
    case 'openai':
      return 'OPENAI_API_KEY';
    case 'anthropic':
      return 'ANTHROPIC_API_KEY';
    case 'gemini':
      return 'GOOGLE_API_KEY';
    case 'cohere':
      return 'COHERE_API_KEY';
    case 'together':
      return 'TOGETHER_API_KEY';
    case 'groq':
      return 'GROQ_API_KEY';
  }
}
