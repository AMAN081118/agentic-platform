// src/utils/Icons.jsx
import {
  Activity,
  Zap,
  BookOpen,
  Sparkles,
  Send as SendIcon,
  Menu as MenuIcon,
  SquarePen,
  MessageSquare,
  Trash2,
} from "lucide-react";

export const Icons = {
  Health: (props) => <Activity size={20} {...props} />,
  Sports: (props) => <Zap size={20} {...props} />,
  Education: (props) => <BookOpen size={20} {...props} />,
  AI: (props) => <Sparkles size={20} {...props} />,
  Send: (props) => <SendIcon size={18} {...props} />,
  Menu: (props) => <MenuIcon size={20} {...props} />,
  Edit: (props) => <SquarePen size={20} {...props} />,
  Message: (props) => <MessageSquare size={16} {...props} />,
  Trash: (props) => <Trash2 size={16} {...props} />,
};
