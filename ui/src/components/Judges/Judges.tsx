import { Accordion, Anchor, Center, Divider, SimpleGrid, Stack, Title, Text, Code } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { useUrlState } from '../../hooks/useUrlState.ts';
import { useJudges } from '../../hooks/useJudges.ts';
import { ConfigureJudgeCard } from './ConfigureJudgeCard.tsx';
import { CreateOllamaJudgeModal } from './CreateOllamaJudgeModal.tsx';
import { CreateProprietaryJudgeModal } from './CreateProprietaryJudgeModal.tsx';
import { CreateFineTunedJudgeModal } from './CreateFineTunedJudgeModal.tsx';
import { JudgeAccordionItem } from './JudgeAccordionItem.tsx';

export function Judges() {
  const { projectSlug } = useUrlState();
  const { data: judges } = useJudges(projectSlug);

  const [isFineTunedOpen, { toggle: toggleFineTuned, close: closeFineTuned }] = useDisclosure(false);
  const [isOllamaOpen, { toggle: toggleOllama, close: closeOllama }] = useDisclosure(false);
  const [isOpenAIOpen, { toggle: toggleOpenAI, close: closeOpenAI }] = useDisclosure(false);
  const [isAnthropicOpen, { toggle: toggleAnthropic, close: closeAnthropic }] = useDisclosure(false);
  const [isGeminiOpen, { toggle: toggleGemini, close: closeGemini }] = useDisclosure(false);
  const [isCohereOpen, { toggle: toggleCohere, close: closeCohere }] = useDisclosure(false);
  const [isTogetherOpen, { toggle: toggleTogether, close: closeTogether }] = useDisclosure(false);
  const [isBedrockOpen, { toggle: toggleBedrock, close: closeBedrock }] = useDisclosure(false);

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
          <ConfigureJudgeCard
            judgeType="together"
            description="Configure a model running on Together AI as a judge"
            onClick={toggleTogether}
          />
          <ConfigureJudgeCard
            judgeType="bedrock"
            description="Configure a model running on AWS Bedrock as a judge"
            onClick={toggleBedrock}
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
        <CreateProprietaryJudgeModal
          isOpen={isTogetherOpen}
          onClose={closeTogether}
          judgeType="together"
          extraCopy={
            <Text inherit>
              Choose any inference model listed in the{' '}
              <Anchor inherit href="https://docs.together.ai/docs/chat-models">
                Together AI documentation
              </Anchor>
              , e.g. <Code>google/gemma-2-9b-it</Code>.
            </Text>
          }
        />
        <CreateProprietaryJudgeModal
          isOpen={isBedrockOpen}
          onClose={closeBedrock}
          judgeType="bedrock"
          modelOptions={[
            'anthropic.claude-3-5-sonnet-20240620-v1:0',
            'anthropic.claude-3-opus-20240229-v1:0',
            'anthropic.claude-3-sonnet-20240229-v1:0',
            'anthropic.claude-3-haiku-20240307-v1:0',
            'cohere.command-r-v1:0',
            'cohere.command-r-plus-v1:0',
            'meta.llama3-8b-instruct-v1:0',
            'meta.llama3-70b-instruct-v1:0',
            'meta.llama3-1-8b-instruct-v1:0',
            'meta.llama3-1-70b-instruct-v1:0',
            'meta.llama3-1-405b-instruct-v1:0',
            'mistral.mistral-large-2402-v1:0',
            'mistral.mistral-large-2407-v1:0',
            'mistral.mistral-small-2402-v1:0',
          ]}
          extraCopy={
            <>
              <Text inherit>
                Models are called using the{' '}
                <Code>
                  <Anchor
                    inherit
                    href="https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html"
                  >
                    Converse
                  </Anchor>
                </Code>{' '}
                API.
              </Text>
              <Text inherit>
                Using Bedrock models requires a valid AWS{' '}
                <Text span inherit fw="bold">
                  authorization
                </Text>{' '}
                and{' '}
                <Text span inherit fw="bold">
                  region
                </Text>{' '}
                configuration in the environment running AutoArena.
              </Text>
            </>
          }
        />
      </Stack>
    </Center>
  );
}
