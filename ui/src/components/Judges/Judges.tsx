import { Accordion, Anchor, Center, Divider, SimpleGrid, Stack, Title, Text, Code } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { ReactNode, useContext } from 'react';
import { useJudges, useUrlState } from '../../hooks';
import { AppConfigContext, ExternalUrls } from '../../lib';
import { ConfigureJudgeCard } from './ConfigureJudgeCard.tsx';
import { CreateJudgeModal } from './CreateJudgeModal.tsx';
import { CreateFineTunedJudgeModal } from './CreateFineTunedJudgeModal.tsx';
import { JudgeAccordionItem } from './JudgeAccordionItem.tsx';
import { JudgeType } from './types.ts';

export function Judges() {
  const { projectSlug } = useUrlState();
  const { data: judges } = useJudges(projectSlug);
  const { enabledJudges } = useContext(AppConfigContext);

  const availableJudges: { [judgeType in JudgeType]: () => ReactNode } = {
    custom: CreateFineTunedJudgeCard,
    openai: CreateOpenAIJudgeCard,
    anthropic: CreateAnthropicJudgeCard,
    ollama: CreateOllamaJudgeCard,
    cohere: CreateCohereJudgeCard,
    gemini: CreateGeminiJudgeCard,
    together: CreateTogetherAIJudgeCard,
    bedrock: CreateBedrockJudgeCard,
    human: () => undefined,
    unrecognized: () => undefined,
  };

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
          {enabledJudges.map(judgeType => availableJudges[judgeType]?.())}
        </SimpleGrid>
      </Stack>
    </Center>
  );
}

function CreateFineTunedJudgeCard() {
  const [isOpen, { toggle, close }] = useDisclosure(false);
  return (
    <div>
      <ConfigureJudgeCard
        judgeType="custom"
        description="Fine-tune a custom judge model on AutoArena"
        onClick={toggle}
      />
      <CreateFineTunedJudgeModal isOpen={isOpen} onClose={close} />
    </div>
  );
}

function CreateOpenAIJudgeCard() {
  const [isOpen, { toggle, close }] = useDisclosure(false);
  return (
    <div>
      <ConfigureJudgeCard
        judgeType="openai"
        description="Configure an OpenAI model like GPT-4o or GPT-4o mini as a judge"
        onClick={toggle}
      />
      <CreateJudgeModal
        isOpen={isOpen}
        onClose={close}
        judgeType="openai"
        modelOptions={['gpt-4o', 'gpt-4o-mini']}
        extraCopy={
          <Text inherit>
            Note that a custom API URL can be used by setting{' '}
            <Code>
              <Anchor inherit href={ExternalUrls.OPENAI_BASE_URL_README} target="_blank">
                OPENAI_BASE_URL
              </Anchor>
            </Code>{' '}
            in the environment running AutoArena.
          </Text>
        }
      />
    </div>
  );
}

function CreateAnthropicJudgeCard() {
  const [isOpen, { toggle, close }] = useDisclosure(false);
  return (
    <div>
      <ConfigureJudgeCard
        judgeType="anthropic"
        description="Configure an Anthropic model like Claude 3.5 Sonnet or Claude 3 Opus as a judge"
        onClick={toggle}
      />
      <CreateJudgeModal
        isOpen={isOpen}
        onClose={close}
        judgeType="anthropic"
        modelOptions={[
          'claude-3-5-sonnet-20240620',
          'claude-3-opus-20240229',
          'claude-3-sonnet-20240229',
          'claude-3-haiku-20240307',
        ]}
      />
    </div>
  );
}

function CreateOllamaJudgeCard() {
  const [isOpen, { toggle, close }] = useDisclosure(false);
  return (
    <div>
      <ConfigureJudgeCard
        judgeType="ollama"
        description="Configure any local Ollama model as a judge"
        onClick={toggle}
      />
      <CreateJudgeModal
        isOpen={isOpen}
        onClose={close}
        judgeType="ollama"
        extraCopy={
          <Stack gap={0}>
            <Text size="sm">
              Enter a model name to use as a judge that runs locally via Ollama. You can specify any model that can be
              downloaded from{' '}
              <Anchor href={ExternalUrls.OLLAMA_MODELS} target="_blank">
                Ollama
              </Anchor>
              . Some examples include:
            </Text>
            <ul>
              <li>
                <Code>llama3.1:8b</Code>
              </li>
              <li>
                <Code>gemma2:9b</Code>
              </li>
              <li>
                <Code>mistral-nemo:12b</Code>
              </li>
            </ul>
            <Text size="sm">
              Note that this model must be pulled via <Code>ollama pull</Code> and the Ollama service must be running on
              the host running AutoArena.
            </Text>
          </Stack>
        }
      />
    </div>
  );
}

function CreateCohereJudgeCard() {
  const [isOpen, { toggle, close }] = useDisclosure(false);
  return (
    <div>
      <ConfigureJudgeCard
        judgeType="cohere"
        description="Configure Command R or Command R+ from Cohere as a judge"
        onClick={toggle}
      />
      <CreateJudgeModal
        isOpen={isOpen}
        onClose={close}
        judgeType="cohere"
        modelOptions={['command-r-plus', 'command-r']}
      />
    </div>
  );
}

function CreateGeminiJudgeCard() {
  const [isOpen, { toggle, close }] = useDisclosure(false);
  return (
    <div>
      <ConfigureJudgeCard
        judgeType="gemini"
        description="Configure a Google Gemini model as a judge"
        onClick={toggle}
      />
      <CreateJudgeModal
        isOpen={isOpen}
        onClose={close}
        judgeType="gemini"
        modelOptions={['gemini-1.5-flash', 'gemini-1.5-pro']}
      />
    </div>
  );
}
function CreateTogetherAIJudgeCard() {
  const [isOpen, { toggle, close }] = useDisclosure(false);
  return (
    <div>
      <ConfigureJudgeCard
        judgeType="together"
        description="Configure a model running on Together AI as a judge"
        onClick={toggle}
      />
      <CreateJudgeModal
        isOpen={isOpen}
        onClose={close}
        judgeType="together"
        extraCopy={
          <Text inherit>
            Choose any inference model listed in the{' '}
            <Anchor inherit href={ExternalUrls.TOGETHER_MODELS} target="_blank">
              Together AI documentation
            </Anchor>
            , e.g. <Code>google/gemma-2-9b-it</Code>.
          </Text>
        }
      />
    </div>
  );
}
function CreateBedrockJudgeCard() {
  const [isOpen, { toggle, close }] = useDisclosure(false);
  return (
    <div>
      <ConfigureJudgeCard
        judgeType="bedrock"
        description="Configure a model running on AWS Bedrock as a judge"
        onClick={toggle}
      />
      <CreateJudgeModal
        isOpen={isOpen}
        onClose={close}
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
                <Anchor inherit href={ExternalUrls.BEDROCK_MODELS} target="_blank">
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
    </div>
  );
}
