'use client';

import { useState } from "react";
import { motion } from "framer-motion";

export default function Contact() {
  const [contactForm, setContactForm] = useState({ name: "", email: "", message: "" });
  const [submitted, setSubmitted] = useState(false);

  const handleContactChange = (e) => {
    const { name, value } = e.target;
    setContactForm(prev => ({ ...prev, [name]: value }));
  };

  const handleContactSubmit = (e) => {
    e.preventDefault();
    console.log("Contact form submitted:", contactForm);
    setSubmitted(true);
    setContactForm({ name: "", email: "", message: "" });
    setTimeout(() => setSubmitted(false), 5000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 text-white relative overflow-hidden">
      
      {/* Background decorative elements */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-16 left-16 w-80 h-80 bg-amber-600/20 rounded-full mix-blend-multiply filter blur-3xl animate-pulse" />
        <div className="absolute bottom-20 right-20 w-80 h-80 bg-indigo-600/20 rounded-full mix-blend-multiply filter blur-3xl animate-pulse" />
      </div>

      <div className="relative pt-24 pb-16 px-6">
        <div className="max-w-2xl mx-auto">

          {/* Form Container */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-12"
          >
            <h1 className="text-4xl font-extrabold text-amber-400 mb-2 tracking-tight">
              Get in Touch
            </h1>
            <p className="text-slate-300 mb-8">
              Have questions or feedback? We'd love to hear from you. Fill out the form below and we'll get back to you as soon as possible.
            </p>

            {/* Submission Success Message */}
            {submitted && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="mb-6 p-4 bg-amber-600/20 border border-amber-400 rounded-xl"
              >
                <p className="text-amber-300 flex items-center gap-2">
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  Thank you for your message! We'll get back to you soon.
                </p>
              </motion.div>
            )}

            {/* Contact Form */}
            <form onSubmit={handleContactSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-amber-400 mb-2">
                  Full Name
                </label>
                <input
                  type="text"
                  name="name"
                  value={contactForm.name}
                  onChange={handleContactChange}
                  required
                  className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500 transition-all duration-200"
                  placeholder="Your name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-amber-400 mb-2">
                  Email Address
                </label>
                <input
                  type="email"
                  name="email"
                  value={contactForm.email}
                  onChange={handleContactChange}
                  required
                  className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500 transition-all duration-200"
                  placeholder="your@email.com"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-amber-400 mb-2">
                  Message
                </label>
                <textarea
                  name="message"
                  value={contactForm.message}
                  onChange={handleContactChange}
                  required
                  rows="6"
                  className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500 resize-none transition-all duration-200"
                  placeholder="Your message..."
                />
              </div>

              <button
                type="submit"
                className="w-full relative overflow-hidden bg-amber-600 text-white font-semibold py-3 px-6 rounded-xl shadow-lg shadow-amber-500/50 hover:shadow-xl hover:shadow-amber-400/70 transform hover:-translate-y-0.5 transition-all duration-200"
              >
                Send Message
                <span className="absolute inset-0 rounded-xl animate-pulse opacity-30 bg-white/20" />
              </button>
            </form>

            <div className="mt-8 pt-8 border-t border-slate-800">
              <p className="text-sm text-slate-400">
                We typically respond to inquiries within 24 hours during business days.
              </p>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
