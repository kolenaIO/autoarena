import { Checkbox, Divider, Group, Input, Modal, MultiSelect, Slider, Stack, Text } from '@mantine/core';
import { useForm } from '@mantine/form';
import { useMemo } from 'react';
import { IconEqual, IconMinus, IconX } from '@tabler/icons-react';
import { useJudges } from '../../hooks/useJudges.ts';
import { useUrlState } from '../../hooks/useUrlState.ts';
import { useHeadToHeadCount } from '../../hooks/useHeadToHeadCount.ts';
import { ConfirmOrCancelBar } from './ConfirmOrCancelBar.tsx';

type Form = {
  judgeIds: string[];
  percent: number; // on [1,100]
  rerun: boolean;
};

type Props = {
  judgeId?: number;
  isOpen: boolean;
  onClose: () => void;
};
export function TriggerAutoJudgeModal({ judgeId, isOpen, onClose }: Props) {
  const { projectSlug } = useUrlState();
  const { data: judges } = useJudges(projectSlug);

  const form = useForm<Form>({
    mode: 'uncontrolled',
    initialValues: { judgeIds: judgeId != null ? [String(judgeId)] : [], percent: 100, rerun: false },
    validateInputOnChange: true,
    validate: { judgeIds: js => (js.length < 1 ? 'Must select at least one judge' : undefined) },
  });

  const formValues = form.getValues();
  const { data: headToHeadCount } = useHeadToHeadCount(projectSlug);

  const autoJudges = useMemo(
    () =>
      (judges ?? [])
        .filter(({ judge_type, enabled }) => judge_type !== 'human' && enabled)
        .map(({ id, name }) => ({ label: name, value: String(id) })),
    [judges]
  );

  function handleSubmit(form: Form) {
    console.log(form);
  }

  function handleClose() {
    form.reset();
    onClose();
  }

  const existingVotes = (judges ?? [])
    .filter(({ id }) => formValues.judgeIds.includes(String(id)))
    .reduce((acc, { n_votes }) => acc + n_votes, 0);
  const nToJudgeFloat =
    (formValues.percent / 100) *
    ((headToHeadCount ?? 0) * formValues.judgeIds.length - (formValues.rerun ? 0 : existingVotes));
  const nToJudge = Math.floor(nToJudgeFloat);
  const showParens = formValues.judgeIds.length > 1 || !formValues.rerun;
  return (
    <Modal opened={isOpen} onClose={handleClose} centered title="Run Automated Judgement" size={540}>
      <form onSubmit={form.onSubmit(handleSubmit)}>
        <Stack gap="lg">
          <Stack gap="xs">
            <MultiSelect
              label="Judges to run"
              description="Select a specific judge or judges to run"
              placeholder={formValues.judgeIds.length < 1 ? 'Select a judge to run' : undefined}
              data={autoJudges}
              flex={1}
              key={form.key('judgeIds')}
              {...form.getInputProps('judgeIds')}
            />
            <Checkbox
              label="Rerun head-to-heads that already have votes"
              key={form.key('rerun')}
              {...form.getInputProps('rerun', { type: 'checkbox' })}
            />
          </Stack>
          <Input.Wrapper
            label="Proportion of head-to-heads"
            description="What proportion of head-to-heads should be judged?"
            mb="md"
          >
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
          <Divider />
          <Stack gap="xs">
            <Text size="sm" fw={500}>
              Approximate number of head-to-heads:
            </Text>
            {headToHeadCount != null && (
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
                {!formValues.rerun && (
                  <>
                    <IconMinus size={18} />
                    <FormulaItem value={existingVotes} label="existing vote" pluralize />
                  </>
                )}
                {showParens && <Text size="xl">)</Text>}
                <IconEqual size={18} />
                <FormulaItem value={nToJudge} label="to run" />
              </Group>
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
