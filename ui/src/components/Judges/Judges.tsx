import { Accordion, Center, Divider, SimpleGrid, Stack, Title } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { useUrlState } from '../../hooks/useUrlState.ts';
import { useJudges } from '../../hooks/useJudges.ts';
import { ConfigureJudgeCard } from './ConfigureJudgeCard.tsx';
import { CreateOllamaJudgeModal } from './CreateOllamaJudgeModal.tsx';
import { CreateProprietaryJudgeModal } from './CreateProprietaryJudgeModal.tsx';
import { CreateFineTunedJudgeModal } from './CreateFineTunedJudgeModal.tsx';
import { JudgeAccordionItem } from './JudgeAccordionItem.tsx';

export function Judges() {
  const { projectId } = useUrlState();
  const { data: judges } = useJudges(projectId);

  const [isFineTunedOpen, { toggle: toggleFineTuned, close: closeFineTuned }] = useDisclosure(false);
  const [isOllamaOpen, { toggle: toggleOllama, close: closeOllama }] = useDisclosure(false);
  const [isOpenAIOpen, { toggle: toggleOpenAI, close: closeOpenAI }] = useDisclosure(false);
  const [isAnthropicOpen, { toggle: toggleAnthropic, close: closeAnthropic }] = useDisclosure(false);
  const [isGeminiOpen, { toggle: toggleGemini, close: closeGemini }] = useDisclosure(false);
  const [isCohereOpen, { toggle: toggleCohere, close: closeCohere }] = useDisclosure(false);

  return (
    <Center p="lg">
      <Stack>
        <Title order={5}>Configured Judges</Title>
        <Accordion variant="contained" w={1080}>
          {(judges ?? []).map(judge => (
            <JudgeAccordionItem key={judge.id} judge={judge} />
          ))}
        </Accordion>

        <Divider />

        <Title order={5}>Configure Automated Judge</Title>
        <SimpleGrid cols={3} w={1080}>
          <ConfigureJudgeCard
            judgeType="custom"
            description="Fine-tune a custom judge model on AutoArena"
            onClick={toggleFineTuned}
          />
          <ConfigureJudgeCard
            judgeType="openai"
            description="Configure an OpenAI model like GPT-4o or GPT-4o mini as a judge"
            onClick={toggleOpenAI}
          />
          <ConfigureJudgeCard
            judgeType="anthropic"
            description="Configure an Anthropic model like Claude 3.5 Sonnet or Claude 3 Opus as a judge"
            onClick={toggleAnthropic}
          />
          <ConfigureJudgeCard
            judgeType="ollama"
            description="Configure any local Ollama model as a judge"
            onClick={toggleOllama}
          />
          <ConfigureJudgeCard
            judgeType="cohere"
            description="Configure Command R or Command R+ from Cohere as a judge"
            onClick={toggleCohere}
          />
          <ConfigureJudgeCard
            judgeType="gemini"
            description="Configure a Google Gemini model as a judge"
            onClick={toggleGemini}
          />
        </SimpleGrid>

        <CreateFineTunedJudgeModal isOpen={isFineTunedOpen} onClose={closeFineTuned} />
        <CreateProprietaryJudgeModal
          isOpen={isOpenAIOpen}
          onClose={closeOpenAI}
          judgeType="openai"
          modelOptions={['gpt-4o', 'gpt-4o-mini']}
        />
        <CreateProprietaryJudgeModal
          isOpen={isAnthropicOpen}
          onClose={closeAnthropic}
          judgeType="anthropic"
          modelOptions={[
            'claude-3-5-sonnet-20240620',
            'claude-3-opus-20240229',
            'claude-3-sonnet-20240229',
            'claude-3-haiku-20240307',
          ]}
        />
        <CreateOllamaJudgeModal isOpen={isOllamaOpen} onClose={closeOllama} />
        <CreateProprietaryJudgeModal
          isOpen={isCohereOpen}
          onClose={closeCohere}
          judgeType="cohere"
          modelOptions={['command-r-plus', 'command-r']}
        />
        <CreateProprietaryJudgeModal
          isOpen={isGeminiOpen}
          onClose={closeGemini}
          judgeType="gemini"
          modelOptions={['gemini-1.5-flash', 'gemini-1.5-pro']}
        />
      </Stack>
    </Center>
  );
}
