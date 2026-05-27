import Navbar from "@/components/marketing/Navbar";
import Hero from "@/components/marketing/Hero";
import StatRow from "@/components/marketing/StatRow";
import LogoStrip from "@/components/marketing/LogoStrip";
import Features from "@/components/marketing/Features";
import FounderCard from "@/components/marketing/FounderCard";
import Plans from "@/components/marketing/Plans";
import TrustStrip from "@/components/marketing/TrustStrip";
import Footer from "@/components/marketing/Footer";

export default function Home() {
  return (
    <main className="min-h-screen bg-white">
      <Navbar />
      <Hero />
      <StatRow />
      <LogoStrip />
      <Features />
      <FounderCard />
      <Plans />
      <TrustStrip />
      <Footer />
    </main>
  );
}
