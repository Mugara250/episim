"use client";

import Link from "next/link";
import { PageMeta } from "@/components/layout/app-shell-context";
import { ImportWizard } from "@/components/population/ImportWizard";

export default function PopulationImportPage() {
  return (
    <>
      <PageMeta title="Import Population Data" subtitle="Configuration Data · Population Data" />
      <div className="flex items-center gap-3">
        <Link href="/data/population" className="text-sm text-text-secondary hover:text-brand-light">
          ← Population Datasets
        </Link>
      </div>
      <h1 className="mt-2 text-2xl font-bold text-text-primary">Import wizard</h1>
      <p className="mt-2 max-w-xl text-sm text-text-secondary">
        Upload a census CSV. The importer detects whether it&apos;s row-per-person microdata or a
        pre-aggregated table from its column headers, validates rows individually, and loads the
        matching storage tier in the background.
      </p>
      <ImportWizard />
    </>
  );
}
