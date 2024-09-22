import { Checkbox, Group, Input, Modal, MultiSelect, Paper, Slider, Stack, Text } from '@mantine/core';
import { useForm } from '@mantine/form';
import { useMemo } from 'react';
import { IconEqual, IconMinus, IconX } from '@tabler/icons-react';
import { useJudges, useUrlState, useHeadToHeadCount, useTriggerAutoJudge } from '../../hooks';
import { ConfirmOrCancelBar } from './ConfirmOrCancelBar.tsx';

type Form = {
  judgeIds: string[];
  percent: number; // on [1,100]
  skipExisting: boolean;
};

type Props = {
  judgeId?: number;
  isOpen: boolean;
  onClose: () => void;
};
export function TriggerAutoJudgeModal({ judgeId, isOpen, onClose }: Props) {
  const { projectSlug = '' } = useUrlState();
  const { data: judges } = useJudges(projectSlug);
  const { mutate: triggerAutoJudge } = useTriggerAutoJudge({ projectSlug });

  const form = useForm<Form>({
    mode: 'uncontrolled',
    initialValues: { judgeIds: judgeId != null ? [String(judgeId)] : [], percent: 100, skipExisting: true },
    validateInputOnChange: true,
    validateInputOnBlur: true,
    validate: { judgeIds: js => (js.length < 1 ? 'Select at least one judge' : undefined) },
  });

  const { data: headToHeadCount } = useHeadToHeadCount(projectSlug);

  const autoJudges = useMemo(
    () =>
      (judges ?? [])
        .filter(({ judge_type }) => judge_type !== 'human')
        .map(({ id, name, enabled }) => ({ label: name, value: String(id), disabled: !enabled })),
    [judges]
  );

  function handleSubmit(form: Form) {
    triggerAutoJudge({
      judge_ids: form.judgeIds.map(judgeId => Number(judgeId)),
      skip_existing: form.skipExisting,
      fraction: form.percent / 100,
    });
    handleClose();
  }

  function handleClose() {
    onClose();
    form.reset();
  }

  // TODO: judgeIds doesn't seem to update always
  const formValues = form.getValues();
  const existingVotes = (judges ?? [])
    .filter(({ id }) => formValues.judgeIds.includes(String(id)))
    .reduce((acc, { n_votes }) => acc + n_votes, 0);
  const nToJudgeFloat =
    (formValues.percent / 100) *
    ((headToHeadCount ?? 0) * formValues.judgeIds.length - (formValues.skipExisting ? existingVotes : 0));
  const nToJudge = Math.ceil(nToJudgeFloat);
  const showParens = formValues.judgeIds.length > 1 || !formValues.skipExisting;
  return (
    <Modal opened={isOpen} onClose={handleClose} centered withCloseButton title="Run Automated Judgement" size={560}>
      <form onSubmit={form.onSubmit(handleSubmit)}>
        <Stack gap="lg">
          <Stack gap="xs">
            <MultiSelect
              label="Select judge or judges to run"
              placeholder={formValues.judgeIds.length < 1 ? 'Select a judge to run' : undefined}
              data={autoJudges}
              flex={1}
              key={form.key('judgeIds')}
              {...form.getInputProps('judgeIds')}
              // manually set onChange as form does not update consistently with the default from form.getInputProps
              onChange={values => form.setFieldValue('judgeIds', values)}
            />
            <Checkbox
              label="Skip head-to-heads with existing votes"
              key={form.key('skipExisting')}
              {...form.getInputProps('skipExisting', { type: 'checkbox' })}
            />
          </Stack>
          <Input.Wrapper label="Percentage of head-to-heads" mb="md">
            <Slider
              min={1}
              marks={[
                { value: 25, label: '25%' },
                { value: 50, label: '50%' },
                { value: 75, label: '75%' },
              ]}
              onChangeEnd={() => form.validate()}
              key={form.key('percent')}
              {...form.getInputProps('percent')}
            />
          </Input.Wrapper>
          <Stack gap="xs">
            <Text size="sm" c="dimmed">
              Approximate number of head-to-heads:
            </Text>
            {headToHeadCount != null && (
              <Paper p="md" bg="gray.1" radius="md">
                <Group gap="xs" justify="center" flex={1}>
                  <FormulaItem value={formValues.percent} label="percent" suffix="%" />
                  <IconX size={18} />
                  {showParens && <Text size="xl">(</Text>}
                  <FormulaItem value={headToHeadCount} label="head-to-head" pluralize />
                  {formValues.judgeIds.length > 1 && (
                    <>
                      <IconX size={18} />
                      <FormulaItem value={formValues.judgeIds.length} label="judge" pluralize />
                    </>
                  )}
                  {formValues.skipExisting && (
                    <>
                      <IconMinus size={18} />
                      <FormulaItem value={existingVotes} label="existing vote" pluralize />
                    </>
                  )}
                  {showParens && <Text size="xl">)</Text>}
                  <IconEqual size={18} />
                  <FormulaItem value={nToJudge} label="to run" />
                </Group>
              </Paper>
            )}
          </Stack>
          <ConfirmOrCancelBar onCancel={handleClose} submitForm={form.isValid() && nToJudge > 0} action="Run" />
        </Stack>
      </form>
    </Modal>
  );
}

function FormulaItem({
  value,
  label,
  pluralize = false,
  suffix,
}: {
  value: number;
  label: string;
  pluralize?: boolean;
  suffix?: string;
}) {
  return (
    <Stack gap={0} align="center">
      <Text>
        {value.toLocaleString()}
        {suffix}
      </Text>
      <Text size="xs" c="dimmed">
        {label}
        {pluralize && value !== 1 ? 's' : ''}
      </Text>
    </Stack>
  );
}
