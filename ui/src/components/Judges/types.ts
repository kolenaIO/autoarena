import {
  IconBrandCoinbase,
  IconBrandGoogle,
  IconBrandOpenai,
  IconDevices2,
  IconLetterA,
  IconRobot,
  IconUsers,
} from '@tabler/icons-react';

export type JudgeType = 'human' | 'ollama' | 'openai' | 'gemini' | 'anthropic' | 'cohere' | 'custom';

export function judgeTypeIconComponent(judgeType: JudgeType) {
  // TODO: get SVGs for real Ollama, Anthropic, and Cohere logos
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
    case 'custom':
    default:
      return IconRobot;
  }
}

export function judgeTypeToCoverImageUrl(judgeType: JudgeType) {
  switch (judgeType) {
    case 'ollama':
      return '/assets/ollama.jpg';
    case 'openai':
      return '/assets/openai.jpg';
    case 'gemini':
      return '/assets/gemini.jpg';
    case 'anthropic':
      return '/assets/anthropic.jpg';
    case 'cohere':
      return '/assets/cohere.jpg';
    case 'custom':
      return '/assets/custom.jpg';
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
  }
}
