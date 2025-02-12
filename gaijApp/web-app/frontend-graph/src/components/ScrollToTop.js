import { useEffect } from "react";
import { useLocation } from "react-router-dom";

const ScrollToTop = () => {
  const { pathname } = useLocation();

  useEffect(() => {
    window.scrollTo(0, 0); // Reset scroll position to the top
  }, [pathname]); // Runs when route changes

  return null;
};

export default ScrollToTop;
