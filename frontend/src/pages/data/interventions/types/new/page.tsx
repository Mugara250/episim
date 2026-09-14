import { InterventionTypeForm } from "@/components/InterventionTypeForm";
import { PageMeta } from "@/components/layout/app-shell-context";
import { createInterventionType } from "@/lib/api";

export default function NewInterventionTypePage() {
  return (
    <>
      <PageMeta title="New Intervention Type" />
      <h1 className="text-2xl font-bold text-text-primary">New Intervention Type</h1>
      <InterventionTypeForm onSubmit={(payload) => createInterventionType(payload).then(() => undefined)} />
    </>
  );
}
