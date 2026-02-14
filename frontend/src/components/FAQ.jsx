'use client';

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

export default function FAQ() {
  const [expandedFAQ, setExpandedFAQ] = useState(null);

  const faqItems = [
    {
      question: "How does the Legal AI Assistant work?",
      answer: "Our AI analyzes legal documents you upload and answers your questions based on verified content. It uses advanced natural language processing to provide accurate legal insights. Simply upload your documents or provide URLs, then ask your questions and get instant answers."
    },
    {
      question: "Is my data secure?",
      answer: "Yes, we use enterprise-grade encryption for all data. Your documents are stored securely and never shared with third parties. We comply with all relevant data protection regulations and standards to ensure your privacy."
    },
    {
      question: "Can this replace my lawyer?",
      answer: "This tool provides legal information and guidance but should not replace professional legal counsel. Always consult with a licensed attorney for critical legal matters, contracts, litigation, or any situation requiring personalized legal advice."
    },
    {
      question: "What file formats do you support?",
      answer: "We support PDF, DOCX, TXT, and other common document formats. You can also provide URLs to legal documents. Our system can handle documents of various sizes, though very large files may take longer to process."
    },
    {
      question: "How long does it take to get an answer?",
      answer: "Most questions are answered within seconds. Complex queries may take up to a minute for thorough analysis. The processing time depends on the document size and complexity of your question."
    },
    {
      question: "What types of legal documents can I upload?",
      answer: "You can upload any legal document including contracts, agreements, policies, statutes, regulations, case law, and more. Our AI is trained on a wide range of legal documents and can analyze most legal texts."
    },
    {
      question: "Is there a limit to how many documents I can upload?",
      answer: "You can upload multiple documents to build a comprehensive knowledge base. However, there are practical limits based on your subscription plan. Free users can upload up to 5 documents, while premium users have higher limits."
    },
    {
      question: "Can I export or download the answers?",
      answer: "Yes, you can export answers in various formats including PDF and text. This makes it easy to share information with colleagues, include in reports, or save for future reference."
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 text-white relative overflow-hidden">
      {/* Background decorative elements */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-16 left-16 w-80 h-80 bg-amber-600/20 rounded-full mix-blend-multiply filter blur-3xl animate-pulse" />
        <div className="absolute bottom-20 right-20 w-80 h-80 bg-indigo-600/20 rounded-full mix-blend-multiply filter blur-3xl animate-pulse" />
      </div>

      <div className="relative pt-24 pb-16 px-6">
        <div className="max-w-4xl mx-auto">

          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="mb-10"
          >
            <h1 className="text-4xl font-extrabold text-amber-400 mb-2 tracking-tight">
              Frequently Asked Questions
            </h1>
            <p className="text-slate-300">
              Find answers to common questions about our Legal AI Assistant platform.
            </p>
          </motion.div>

          {/* FAQ Items */}
          <div className="space-y-4">
            {faqItems.map((item, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: idx * 0.05 }}
                className="bg-slate-900 rounded-xl border border-slate-800 overflow-hidden shadow-lg"
              >
                <button
                  onClick={() => setExpandedFAQ(expandedFAQ === idx ? null : idx)}
                  className="w-full px-8 py-5 flex items-center justify-between hover:bg-slate-800 transition-all duration-200 text-left cursor-pointer"
                >
                  <h3 className="font-semibold text-amber-400 text-lg">
                    {item.question}
                  </h3>
                  <svg
                    className={`w-6 h-6 text-amber-300 transition-transform duration-200 flex-shrink-0 ${
                      expandedFAQ === idx ? "transform rotate-180" : ""
                    }`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 14l-7 7m0 0l-7-7m7 7V3"
                    />
                  </svg>
                </button>
                <AnimatePresence>
                  {expandedFAQ === idx && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: "auto" }}
                      exit={{ opacity: 0, height: 0 }}
                      transition={{ duration: 0.3 }}
                      className="px-8 py-5 border-t border-slate-800 bg-slate-950 text-slate-300"
                    >
                      {item.answer}
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            ))}
          </div>

          {/* Contact Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mt-12 p-8 bg-slate-900 rounded-2xl shadow-lg border border-slate-800"
          >
            <h2 className="text-2xl font-bold text-amber-400 mb-4">
              Didn't find your answer?
            </h2>
            <p className="text-slate-300 mb-6">
              If you have additional questions or need further assistance, please don't hesitate to reach out to our support team.
            </p>
            <a
              href="/contact"
              className="inline-block bg-amber-600 text-black font-semibold py-3 px-6 rounded-xl shadow-lg shadow-amber-500/50 hover:shadow-xl hover:shadow-amber-400/70 transform hover:-translate-y-0.5 transition-all duration-200"
            >
              Contact Us
            </a>
          </motion.div>

        </div>
      </div>
    </div>
  );
}
