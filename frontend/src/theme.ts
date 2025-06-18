import { createTheme } from '@mui/material/styles';

// Snort's brand colors
const snortRed = '#FF0000';
const snortBlack = '#000000';
const snortWhite = '#FFFFFF';
const snortGray = '#333333';

export const theme = createTheme({
  palette: {
    primary: {
      main: snortRed,
      contrastText: snortWhite,
    },
    secondary: {
      main: snortBlack,
      contrastText: snortWhite,
    },
    background: {
      default: snortWhite,
      paper: snortWhite,
    },
    text: {
      primary: snortBlack,
      secondary: snortGray,
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 700,
      color: snortRed,
    },
    h2: {
      fontWeight: 600,
      color: snortBlack,
    },
    h3: {
      fontWeight: 600,
      color: snortBlack,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 4,
          textTransform: 'none',
          fontWeight: 600,
        },
        contained: {
          boxShadow: 'none',
          '&:hover': {
            boxShadow: 'none',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        },
      },
    },
  },
}); 