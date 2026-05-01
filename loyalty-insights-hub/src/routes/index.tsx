import { createFileRoute } from "@tanstack/react-router";
import { LoyaltyApp } from "@/components/loyalty/LoyaltyApp";
import { Toaster } from "@/components/ui/sonner";

export const Route = createFileRoute("/")({
  component: Index,
  head: () => ({
    meta: [
      { title: "Loyalty Analytics Agent" },
      { name: "description", content: "Conversational AI analytics for loyalty data — ask questions in plain English." },
    ],
  }),
});

function Index() {
  return (
    <>
      <LoyaltyApp />
      <Toaster position="top-right" theme="dark" richColors closeButton />
    </>
  );
}
