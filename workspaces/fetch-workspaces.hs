{-# LANGUAGE FlexibleContexts #-}

import XMonad
import qualified XMonad.StackSet as W
import Control.Monad
import System.IO

main :: X ()
main = do
    ws <- gets windowset
    let currentWorkspace = W.currentTag ws
    let allWorkspaces = W.workspaces ws
    liftIO $ forM_ allWorkspaces $ \w -> do
        let tag = W.tag w
        let marker = if tag == currentWorkspace then " *" else ""
        putStrLn (tag ++ marker ++ "\n")
