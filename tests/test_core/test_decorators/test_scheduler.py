import pytest
import time
from unittest.mock import patch, MagicMock

from nest.core.decorators.scheduler import Cron, Interval
from nest.core.apscheduler.enums.cron_expression import CronExpression
from nest.core.apscheduler import scheduler


class TestSchedulerDecorators:
    """Tests for task scheduling decorators."""
    
    def setup_method(self):
        """Setup executed before each test."""
        # Clear all jobs from scheduler
        scheduler.remove_all_jobs()
    
    def teardown_method(self):
        """Cleanup executed after each test."""
        # Remove all jobs from scheduler
        scheduler.remove_all_jobs()
    
    @patch('nest.core.decorators.scheduler.scheduler')
    def test_cron_decorator_valid_expression(self, mock_scheduler):
        """Tests the @Cron decorator with valid expression."""
        # Arrange
        mock_scheduler.add_job = MagicMock()
        
        # Act
        @Cron(expression=CronExpression.EVERY_MINUTE)
        def test_function():
            return "test"
        
        result = test_function()
        
        # Assert
        assert result == "test"
        mock_scheduler.add_job.assert_called_once()
        call_args = mock_scheduler.add_job.call_args
        assert call_args[0][0] == test_function
        assert call_args[1]['trigger'] == CronExpression.EVERY_MINUTE.value
        assert 'id' in call_args[1]
    
    def test_cron_decorator_invalid_expression(self):
        """Tests the @Cron decorator with invalid expression."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid cron expression"):
            @Cron(expression="invalid")
            def test_function():
                return "test"
    
    @patch('nest.core.decorators.scheduler.scheduler')
    def test_interval_decorator_with_seconds(self, mock_scheduler):
        """Tests the @Interval decorator with seconds."""
        # Arrange
        mock_scheduler.add_job = MagicMock()
        
        # Act
        @Interval(seconds=30)
        def test_function():
            return "test"
        
        result = test_function()
        
        # Assert
        assert result == "test"
        mock_scheduler.add_job.assert_called_once()
        call_args = mock_scheduler.add_job.call_args
        assert call_args[0][0] == test_function
        assert call_args[1]['trigger'] == 'interval'
        assert call_args[1]['seconds'] == 30
    
    @patch('nest.core.decorators.scheduler.scheduler')
    def test_interval_decorator_with_minutes(self, mock_scheduler):
        """Tests the @Interval decorator with minutes."""
        # Arrange
        mock_scheduler.add_job = MagicMock()
        
        # Act
        @Interval(minutes=5)
        def test_function():
            return "test"
        
        result = test_function()
        
        # Assert
        assert result == "test"
        mock_scheduler.add_job.assert_called_once()
        call_args = mock_scheduler.add_job.call_args
        assert call_args[1]['minutes'] == 5
    
    def test_interval_decorator_no_parameters(self):
        """Tests the @Interval decorator without parameters."""
        # Act & Assert
        with pytest.raises(ValueError, match="At least one time parameter must be provided"):
            @Interval()
            def test_function():
                return "test"
    
    @patch('nest.core.decorators.scheduler.scheduler')
    def test_interval_decorator_multiple_parameters(self, mock_scheduler):
        """Tests the @Interval decorator with multiple parameters."""
        # Arrange
        mock_scheduler.add_job = MagicMock()
        
        # Act
        @Interval(seconds=30, minutes=1, hours=2)
        def test_function():
            return "test"
        
        result = test_function()
        
        # Assert
        assert result == "test"
        mock_scheduler.add_job.assert_called_once()
        call_args = mock_scheduler.add_job.call_args
        assert call_args[1]['seconds'] == 30
        assert call_args[1]['minutes'] == 1
        assert call_args[1]['hours'] == 2