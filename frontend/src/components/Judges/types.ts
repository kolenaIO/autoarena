import {
  IconBrandCoinbase,
  IconBrandGoogle,
  IconBrandOpenai,
  IconDevices2,
  IconLetterA,
  IconRobot,
  IconUsers,
} from '@tabler/icons-react';
import { Judge } from '../../hooks/useJudges.ts';

export function judgeTypeIconComponent(judgeType: Judge['judge_type']) {
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
      return IconLetterA; // TODO
    case 'cohere':
      return IconBrandCoinbase; // TODO
    case 'custom':
    default:
      return IconRobot;
  }
}

export function judgeTypeToCoverImageUrl(judgeType: Judge['judge_type']) {
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

export function judgeTypeToHumanReadableName(judgeType: Judge['judge_type']) {
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
