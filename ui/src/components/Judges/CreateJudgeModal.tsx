import { ReactNode, useEffect, useMemo, useState } from 'react';
import { Autocomplete, Modal, Stack, Text, TextInput, Transition } from '@mantine/core';
import { useForm } from '@mantine/form';
import { useUrlState, useCreateJudge, useJudges } from '../../hooks';
import { JudgeType, judgeTypeToHumanReadableName } from './types.ts';
import { ConfirmOrCancelBar } from './ConfirmOrCancelBar.tsx';
import { ConfigureSystemPromptCollapse } from './ConfigureSystemPromptCollapse.tsx';
import { CanAccessJudgeStatusIndicator } from './CanAccessJudgeStatusIndicator.tsx';

type Form = {
  modelName: string;
  name: string;
  systemPrompt: string;
};

type Props = {
  judgeType: JudgeType;
  modelOptions?: string[];
  isOpen: boolean;
  onClose: () => void;
  extraCopy?: ReactNode;
};
export function CreateJudgeModal({ judgeType, modelOptions, isOpen, onClose, extraCopy }: Props) {
  const { projectSlug = '' } = useUrlState();
  const { data: judges } = useJudges(projectSlug);
  const { mutate: createJudge } = useCreateJudge({ projectSlug });
  const [showNameInput, setShowNameInput] = useState(false);

  const existingJudgeNames = useMemo(() => new Set((judges ?? []).map(({ name }) => name)), [judges]);

  const form = useForm<Form>({
    mode: 'uncontrolled',
    initialValues: { name: '', modelName: '', systemPrompt: '' },
    onValuesChange: ({ modelName }, { modelName: prevModelName }) => {
      if (modelName !== prevModelName) {
        form.setFieldValue('name', modelName);
      }
    },
    validate: {
      name: n => (n === '' ? 'Name cannot be empty' : existingJudgeNames.has(n) ? 'Name must be unique' : undefined),
      modelName: n => (n === '' ? 'Model name cannot be empty' : undefined),
    },
    validateInputOnChange: true,
  });
  const { modelName, systemPrompt } = form.getValues();

  useEffect(() => {
    if (modelName !== '') {
      setShowNameInput(true);
    }
  }, [modelName]);

  function handleClose() {
    onClose();
    setShowNameInput(false);
    form.reset();
  }

  function handleSubmit({ name, modelName, systemPrompt }: Form) {
    createJudge({
      judge_type: judgeType,
      name,
      model_name: modelName,
      system_prompt: systemPrompt,
      description: `${judgeTypeToHumanReadableName(judgeType)} judge using '${modelName}' via API`,
    });
    handleClose();
  }

  const modelNameSuggestions = modelOptions != null ? [{ group: 'Recommended', items: modelOptions }] : [];
  return (
    <Modal
      opened={isOpen}
      onClose={handleClose}
      centered
      title={<Text fw={500}>Create {judgeTypeToHumanReadableName(judgeType)} Judge</Text>}
    >
      <form onSubmit={form.onSubmit(handleSubmit)}>
        <Stack fz="sm">
          <Text inherit>Call the {judgeTypeToHumanReadableName(judgeType)} API as a judge.</Text>
          {extraCopy}
          <Autocomplete
            label="Model Name"
            placeholder="Enter model name"
            data={modelNameSuggestions}
            flex={1}
            key={form.key('modelName')}
            {...form.getInputProps('modelName')}
          />
          <Transition mounted={isOpen && showNameInput} transition="slide-right" duration={200} timingFunction="ease">
            {transitionStyle => (
              <TextInput
                style={transitionStyle}
                label="Name"
                description="Change this to use the same model with different system prompts"
                defaultValue={modelName}
                placeholder="Enter name"
                flex={1}
                key={form.key('name')}
                {...form.getInputProps('name')}
              />
            )}
          </Transition>
          <ConfigureSystemPromptCollapse
            value={systemPrompt}
            setValue={value => form.setFieldValue('systemPrompt', value)}
          />
          <CanAccessJudgeStatusIndicator judgeType={judgeType} />
          <ConfirmOrCancelBar onCancel={handleClose} submitForm={form.isValid()} action="Create" />
        </Stack>
      </form>
    </Modal>
  );
}
