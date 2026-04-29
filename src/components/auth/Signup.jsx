import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  createUserWithEmailAndPassword,
  updateProfile,
} from "firebase/auth";
import { User, Mail, Lock, Loader2, CheckCircle2 } from "lucide-react";
import { auth } from "./Firebase";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";

const Signup = () => {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [stage, setStage] = useState(1);
  const navigate = useNavigate();

  const validatePassword = () => {
    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return false;
    }
    if (password.length < 6) {
      setError("Password should be at least 6 characters");
      return false;
    }
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!validatePassword()) return;

    setLoading(true);

    try {
      const userCredential = await createUserWithEmailAndPassword(
        auth,
        email,
        password,
      );
      await updateProfile(userCredential.user, { displayName: name });
      setStage(2);
      setTimeout(() => navigate("/dashboard/upload"), 1200);
    } catch (err) {
      setError(err.message);
      setLoading(false);
      console.error("Signup error:", err);
    }
  };

  return (
    <div className="flex min-h-[100dvh] items-center justify-center p-6 md:p-10">
      <div className="w-full max-w-[440px] animate-fade-in">
        <div className="mb-8 text-center">
          <p className="font-display text-xs font-semibold uppercase tracking-[0.35em] text-plum">
            LexiHire
          </p>
          <h1 className="mt-2 font-display text-3xl font-semibold tracking-tight text-foreground md:text-4xl">
            Create your account
          </h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Minimal setup — then upload and rank in one flow.
          </p>
        </div>

        <Card className="border-border/60 shadow-md shadow-plum/5 backdrop-blur-sm">
          {stage === 1 ? (
            <>
              <CardHeader className="space-y-1 pb-2">
                <CardTitle className="text-xl">Sign up</CardTitle>
                <CardDescription>
                  We only store what Firebase needs for auth.
                </CardDescription>
              </CardHeader>
              <CardContent>
                {error ? (
                  <Alert variant="destructive" className="mb-4">
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                ) : null}

                <form onSubmit={handleSubmit} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Full name</Label>
                    <div className="relative">
                      <User
                        className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground"
                        aria-hidden
                      />
                      <Input
                        id="name"
                        type="text"
                        autoComplete="name"
                        placeholder="Alex Morgan"
                        className="pl-9"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        required
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    <div className="relative">
                      <Mail
                        className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground"
                        aria-hidden
                      />
                      <Input
                        id="email"
                        type="email"
                        autoComplete="email"
                        placeholder="you@company.com"
                        className="pl-9"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="password">Password</Label>
                    <div className="relative">
                      <Lock
                        className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground"
                        aria-hidden
                      />
                      <Input
                        id="password"
                        type="password"
                        autoComplete="new-password"
                        placeholder="At least 6 characters"
                        className="pl-9"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="confirm-password">Confirm password</Label>
                    <div className="relative">
                      <Lock
                        className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground"
                        aria-hidden
                      />
                      <Input
                        id="confirm-password"
                        type="password"
                        autoComplete="new-password"
                        placeholder="Repeat password"
                        className="pl-9"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        required
                      />
                    </div>
                  </div>

                  <Button type="submit" className="w-full" disabled={loading}>
                    {loading ? (
                      <>
                        <Loader2 className="size-4 animate-spin" />
                        Creating…
                      </>
                    ) : (
                      "Create account"
                    )}
                  </Button>
                </form>
              </CardContent>
              <CardFooter className="flex flex-col border-t border-border/60 bg-muted/30 py-4">
                <p className="text-center text-sm text-muted-foreground">
                  Already registered?{" "}
                  <Link
                    to="/login"
                    className="font-medium text-plum no-underline hover:underline"
                  >
                    Sign in
                  </Link>
                </p>
              </CardFooter>
            </>
          ) : (
            <CardContent className="flex flex-col items-center gap-4 py-14 text-center">
              <div className="flex size-14 items-center justify-center rounded-full bg-accent/25 text-accent-foreground ring-8 ring-accent/10">
                <CheckCircle2 className="size-7" aria-hidden />
              </div>
              <div>
                <CardTitle className="text-xl">You&apos;re in</CardTitle>
                <CardDescription className="mt-2 text-base">
                  Redirecting to your workspace…
                </CardDescription>
              </div>
              <Loader2 className="size-5 animate-spin text-muted-foreground" />
            </CardContent>
          )}
        </Card>
      </div>
    </div>
  );
};

export default Signup;
