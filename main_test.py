import unittest
import discord
from discord.ext import commands

import os
import sys
from unittest import mock

from main import AutoGanj


class TestAutoGanj(unittest.TestCase):
    """Test the AutoGanj class."""

    def setUp(self):
        """Set up the test."""
        self.bot = AutoGanj()

    @mock.patch('discord.ext.commands.Bot.run')
    def test_start(self, mock_run):
        """Test the start method."""
        self.bot.start("token")
        mock_run.assert_called_once_with("token")

    @mock.patch('discord.ext.commands.Bot.load_extension')
    async def test_load_extensions(self, mock_load_extension):
        """Test the load_extensions method."""
        await self.bot.load_extensions()
        mock_load_extension.assert_called()

    @mock.patch('discord.ext.commands.Bot.add_cog')
    async def test_add_view(self, mock_add_cog):
        """Test the add_view method."""
        view = mock.MagicMock()
        await self.bot.add_view(view)
        mock_add_cog.assert_called()

    @mock.patch('discord.ext.commands.Bot.get_channel')
    async def test_on_error(self, mock_get_channel):
        """Test the on_error method."""
        await self.bot.on_error("event", "arg1", "arg2")
        mock_get_channel.assert_called()

    @mock.patch('discord.ext.commands.Bot.get_channel')
    async def test_on_command_error(self, mock_get_channel):
        """Test the on_command_error method."""
        ctx = mock.MagicMock()
        error = mock.MagicMock()
        await self.bot.on_command_error(ctx, error)
        mock_get_channel.assert_called()

    @mock.patch('discord.ext.commands.Bot.get_channel')
    async def test_on_ready(self, mock_get_channel):
        """Test the on_ready method."""
        await self.bot.on_ready()
        mock_get_channel.assert_called()


if __name__ == '__main__':
    unittest.main()