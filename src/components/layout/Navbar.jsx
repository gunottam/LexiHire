import React from "react";
import { NavLink } from "react-router-dom";
import { Upload } from "lucide-react";
import { cn } from "@/lib/utils";

const Navbar = () => {
  return (
    <header className="sticky top-0 z-40 border-b border-border/70 bg-card/80 backdrop-blur-md">
      <div className="mx-auto flex h-14 max-w-5xl items-center justify-between px-4 sm:px-6">
        <div className="flex items-center gap-2">
          <span className="flex size-8 items-center justify-center rounded-lg bg-plum text-xs font-bold tracking-tight text-plum-foreground">
            LH
          </span>
          <div className="leading-tight">
            <p className="font-display text-sm font-semibold tracking-tight text-foreground">
              LexiHire
            </p>
            <p className="text-[11px] text-muted-foreground">Resume compiler</p>
          </div>
        </div>

        <nav className="flex items-center gap-1">
          <NavLink
            to="/dashboard/upload"
            className={({ isActive }) =>
              cn(
                "inline-flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-secondary text-secondary-foreground shadow-sm"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground",
              )
            }
            end
          >
            <Upload className="size-4" aria-hidden />
            Upload
          </NavLink>
        </nav>
      </div>
    </header>
  );
};

export default Navbar;
